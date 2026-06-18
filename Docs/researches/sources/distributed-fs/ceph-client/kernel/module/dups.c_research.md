# sources/distributed-fs/ceph-client/kernel/module/dups.c

## Purpose
Suppresses duplicate in-kernel module autoload requests so concurrent `request_module()` calls for the same module do not trigger repeated userspace `modprobe` and repeated `finit_module` memory pressure.

## Important APIs, Types, And Functions
Exports internal helpers `kmod_dup_request_exists_wait` and `kmod_dup_request_announce`. State is represented by `struct kmod_dup_req`, the RCU-protected `dup_kmod_reqs` list, `kmod_dup_mutex`, `first_req_done`, `complete_work`, and `delete_work`. The boot/module parameter `module.enable_dups_trace` controls WARN versus warning logging.

## Control Flow
Before launching modprobe, `__request_module` asks `kmod_dup_request_exists_wait`. A synchronous first request inserts an entry; duplicate synchronous callers wait for completion and reuse the first return value; duplicate nowait callers return success immediately. When modprobe completes, `kmod_dup_request_announce` stores the result and queues completion work, which wakes waiters and later schedules deletion of the tracking entry.

## State And Persistence
Tracking entries persist briefly in memory after completion and are deleted by delayed work after about 60 seconds. No durable persistence exists.

## Dependencies And Integration Points
Depends on workqueues, completions, RCU lists, mutexes, module parameters, and `internal.h`. It is called from `kmod.c` around userspace helper execution and configured by `CONFIG_MODULE_DEBUG_AUTOLOAD_DUPS`.

## Risks And Edge Cases
The first nowait request cannot anchor a synchronous wait because it has no meaningful result to share. Entry deletion is heuristic, so late repeated requests can still reach userspace. Return sharing must not complete before the first caller records the result. String length handling assumes module names fit `MODULE_NAME_LEN`.

## Test Signals
Concurrent `request_module()` storms should emit duplicate warnings, avoid repeated synchronous modprobe work, and return consistent status to waiters. Tests should cover nowait first requests, wait first requests, killable waits, trace mode, and delayed deletion.

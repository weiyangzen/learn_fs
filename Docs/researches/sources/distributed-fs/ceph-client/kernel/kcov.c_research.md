# sources/distributed-fs/ceph-client/kernel/kcov.c

## Purpose
Implements KCOV coverage collection for fuzzing through a debugfs device. It records instrumented PCs or comparison operands for the current task, and supports remote coverage sections for background threads and softirqs.

## Important APIs, Types, and Functions
`struct kcov` tracks device state, buffer, owner task, remote mode, refcount, and sequence. Remote state uses `struct kcov_remote`, `struct kcov_remote_area`, and per-CPU `struct kcov_percpu_data`. Instrumentation entry points include `__sanitizer_cov_trace_pc`, comparison callbacks, and switch tracing. User API is through `kcov_open`, `kcov_mmap`, `kcov_ioctl`, `kcov_close`; remote kernel API exports `kcov_remote_start`, `kcov_remote_stop`, and `kcov_common_handle`.

## Control Flow
Users open `/sys/kernel/debug/kcov`, call `KCOV_INIT_TRACE`, mmap the buffer, then enable PC or CMP mode. Instrumented callbacks check task mode and append records into the shared buffer. Disable resets task state and drops the active reference. Remote enable registers handles in a hash table; `kcov_remote_start` looks up a handle, installs a temporary per-task/per-CPU coverage area, and `kcov_remote_stop` merges records into the owning buffer if the sequence still matches.

## State and Persistence
State persists while the debugfs fd, enabled task, or remote section holds a refcount. Coverage buffers are vmalloc-backed and user-mapped. Remote area caches are kept in a global list, and per-CPU IRQ areas are allocated at init. No data survives close or reboot.

## Dependencies and Integration Points
Depends on compiler sanitizer coverage hooks, debugfs, vmalloc mmap insertion, task_struct KCOV fields, KMSAN unpoisoning, local locks, softirq context checks, and subsystem handle definitions from `linux/kcov.h`.

## Risks
Mode transitions must prevent multiple tasks from using one kcov object. Ordering barriers protect callback readers from partially installed task state. Remote start cannot take `kcov->lock` under `kcov_remote_lock`, so sequence checks defend against disable races. Buffer count updates need write barriers before userspace observes new records.

## Test Signals
`CONFIG_KCOV_SELFTEST` checks interrupt filtering by enabling tracing without a buffer and waiting for timer interrupts. Runtime validation is mostly userspace fuzzing tests exercising debugfs ioctls, mmap sizing, remote handles, and record formats.

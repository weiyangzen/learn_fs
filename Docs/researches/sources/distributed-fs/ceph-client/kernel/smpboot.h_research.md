# sources/distributed-fs/ceph-client/kernel/smpboot.h

## Purpose
`smpboot.h` is the local kernel header for SMP boot helpers implemented in `smpboot.c`. It exposes idle-thread setup only when generic SMP idle threads are configured and declares hotplug thread lifecycle hooks used by CPU hotplug code.

## Important APIs, types, and functions
- `struct task_struct` forward declaration avoids pulling scheduler internals into every includer.
- `idle_thread_get()`, `idle_thread_set_boot_cpu()`, `idle_threads_init()` are real declarations under `CONFIG_GENERIC_SMP_IDLE_THREAD` and no-op/NULL inlines otherwise.
- `smpboot_create_threads()`, `smpboot_park_threads()`, `smpboot_unpark_threads()` are CPU-specific hotplug lifecycle calls.
- `cpuhp_threads_init()` is declared as an init-time CPU hotplug thread setup hook.

## Control flow
The header itself has no runtime control flow, but its config guards select either real idle-thread helpers or inert stubs. That lets generic code compile across architectures that do not use the common idle-thread implementation.

## State and persistence
No state is defined here. State lives in `smpboot.c` or in descriptors owned by users of the public `linux/smpboot.h` API.

## Dependencies and integration points
The header is included by common SMP bring-up code and indirectly supports subsystem integration with CPU hotplug. It must stay synchronized with `smpboot.c` function definitions and the CPU hotplug state machine.

## Risks
The main risk is declaration drift: mismatched init attributes or function signatures would break early-boot/hotplug code. The fallback `idle_thread_get()` returns `NULL`, so callers must only rely on it where generic idle threads are enabled or handle the stub result.

## Test signals
Build coverage across `CONFIG_GENERIC_SMP_IDLE_THREAD=y/n` is the primary signal. CPU hotplug boot tests validate that the declared lifecycle hooks are wired to definitions.

# sources/distributed-fs/ceph-client/kernel/smpboot.c

## Purpose
`smpboot.c` provides common SMP CPU bring-up/teardown helpers for idle threads and per-CPU hotplug kthreads. It lets subsystems describe a `struct smp_hotplug_thread` and receive one parked/unparked kernel thread per CPU as CPUs become online or offline.

## Important APIs, types, and functions
- `idle_thread_get()`, `idle_thread_set_boot_cpu()`, `idle_threads_init()`: manage per-CPU idle task pointers when `CONFIG_GENERIC_SMP_IDLE_THREAD` is enabled.
- `struct smpboot_thread_data`: per-created-thread private state containing CPU id, lifecycle status, and owning `struct smp_hotplug_thread`.
- `smpboot_thread_fn()`: generic body for registered hotplug threads. It handles stop, park, setup, unpark, sleep, and runnable callbacks.
- `smpboot_create_threads()`, `smpboot_park_threads()`, `smpboot_unpark_threads()`: CPU hotplug entry points that iterate all registered descriptors.
- `smpboot_register_percpu_thread()` / `smpboot_unregister_percpu_thread()`: exported registration API for subsystems such as softirq and stop-machine.

## Control flow
Idle initialization stores the boot CPU's current task and calls `fork_idle()` for every other possible CPU. Hotplug thread registration acquires `cpus_read_lock()` and `smpboot_threads_lock`, creates a parked kthread on every online CPU, unparks it, then adds the descriptor to `hotplug_threads`. The per-thread loop transitions from `HP_THREAD_NONE` to `HP_THREAD_ACTIVE` through optional `setup()`, responds to `kthread_should_park()` through optional `park()` and `kthread_parkme()`, responds to stop by running optional `cleanup()`, and otherwise sleeps until `thread_should_run()` permits `thread_fn()` to execute on the bound CPU.

## State and persistence
Persistent runtime state is all in-kernel: `idle_threads` per-CPU task pointers, `hotplug_threads` global list, per-descriptor task storage addressed by `ht->store`, and each thread's `HP_THREAD_*` status. Threads for offline CPUs are kept parked so they can be reused, and `smpboot_destroy_threads()` stops possible-CPU threads on unregister.

## Dependencies and integration points
This file depends on CPU hotplug locks, percpu storage, kthreads, scheduler CPU binding, and `linux/smpboot.h`. It is consumed by per-CPU worker subsystems including `softirq.c` (`ksoftirqd` and optional `ktimers`) and `stop_machine.c` (`migration/%u` stopper threads). `wait_task_inactive(TASK_PARKED)` is used before `create()` callbacks that require the task to be off-runqueue.

## Risks
Lifecycle callbacks must tolerate exact CPU affinity and the status transitions enforced here. `BUG_ON(td->cpu != smp_processor_id())` turns CPU-affinity violations into fatal errors. `selfparking` descriptors are not unparked/parked by generic helpers, so descriptor authors must implement their own synchronization. Registration failure destroys threads already created for that descriptor.

## Test signals
Useful validation is CPU hotplug stress with registered users (`ksoftirqd`, stopper threads), boot on SMP and UP-like configs, and lockdep coverage of the register/unregister paths. Failures usually appear as missing per-CPU threads, warnings from `wait_task_inactive()`, CPU mismatch `BUG_ON()`, or hotplug stalls.

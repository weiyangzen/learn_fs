<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smpboot.h -->
# sources/distributed-fs/ceph-client/include/linux/smpboot.h

## Purpose
`smpboot.h` declares the generic framework for per-CPU hotplug threads. It lets subsystems register a descriptor so the kernel can create, park, unpark, run, and clean up one thread per CPU as CPUs come online or offline.

## Important APIs, Types, and Functions
The main type is `struct smp_hotplug_thread`. It contains a per-CPU task pointer store, list linkage for core management, callbacks `thread_should_run`, `thread_fn`, `create`, `setup`, `cleanup`, `park`, and `unpark`, a `selfparking` flag, and `thread_comm` base name. The public APIs are `smpboot_register_percpu_thread()` and `smpboot_unregister_percpu_thread()`.

## Control Flow
A subsystem fills a static `smp_hotplug_thread` descriptor and registers it. The SMP boot/hotplug core creates per-CPU kernel threads, calls optional create/setup callbacks at creation or first operation, repeatedly asks `thread_should_run()` with preemption disabled, and invokes `thread_fn()` for work. CPU offline events park threads and may call `park`; CPU online events unpark them and may call `unpark`. Unregistration stops and cleans up the registered thread family.

## State and Persistence Behavior
State persists in the registered descriptor and the per-CPU `task_struct` pointers referenced by `store`. Threads exist while the descriptor is registered and CPUs are present/online according to hotplug state. Callback-owned subsystem state must handle CPU online/offline transitions. No disk persistence exists.

## Dependencies and Integration Points
The header depends on kernel types and forward-declared `struct task_struct`. It integrates with the CPU hotplug core, scheduler, kthread infrastructure, per-CPU storage, and subsystems that need CPU-local worker threads such as watchdogs, migration helpers, or networking/RCU-adjacent workers.

## Risks and Test Signals
Risks include callback sleep/preemption violations, failing to park or clean up CPU-local resources, stale per-CPU task pointers, unregister races with hotplug, and incorrect `selfparking` behavior. Test signals include CPU hotplug stress, lockdep in callbacks, kthread lifecycle tracing, subsystem-specific online/offline tests, and verifying no per-CPU threads remain after unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smpboot.h -->

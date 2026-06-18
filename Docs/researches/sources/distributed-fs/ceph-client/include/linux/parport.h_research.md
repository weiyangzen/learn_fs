# Research: sources/distributed-fs/ceph-client/include/linux/parport.h

Purpose: `parport.h` is the public kernel interface for the parallel-port core. It models low-level port operations, high-level parport drivers, attached devices, IEEE1284 protocol state, ownership arbitration, proc/device-model integration, and architecture-specific dispatch.

Important APIs/types/functions: key types include `struct parport_operations`, `struct pardevice`, `enum ieee1284_phase`, `struct ieee1284_info`, `struct parport`, `struct parport_driver`, and `struct pardev_cb`. APIs include port register/announce/remove, driver register/unregister, port lookup, refcounting, device register/unregister, `parport_claim()`, `parport_claim_or_block()`, `parport_release()`, `parport_yield()`, `parport_yield_blocking()`, IEEE1284 read/write/negotiate helpers, daisy-chain helpers, proc registration, and generic IRQ handling.

Control flow and state: low-level drivers register a `parport` with register access callbacks, announce it, and high-level drivers attach devices. Devices arbitrate ownership through claim/release and may be preempted or woken by resource management. `parport_yield*()` releases and reclaims only when waiters exist and the device timeslice expired. State includes current active device, wait queue, locks, IEEE1284 phase, probe info, mux/daisy selection, default timeslice, and per-device saved port state.

Dependencies and integration points: depends on jiffies, procfs, spin/rw locks, wait queues, semaphores, device model, IRQ handling, architecture ptrace, UAPI parport constants, and optionally `parport_pc.h` for direct PC fast paths.

Risks and test signals: risks include ownership misuse after release, IRQ callback races under `cad_lock`, deadlocks in preempt/wakeup callbacks, incorrect mux/daisy state, and driver/device lifetime refcount bugs. Tests should cover multi-device contention, blocking and nonblocking claim, IEEE1284 phase transitions, IRQ dispatch, proc registration, hotplug detach, and PC-vs-generic dispatch builds.

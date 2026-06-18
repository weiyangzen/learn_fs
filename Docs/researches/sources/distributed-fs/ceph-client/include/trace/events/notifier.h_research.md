# sources/distributed-fs/ceph-client/include/trace/events/notifier.h

Purpose: Defines trace events for kernel notifier-chain registration, unregistration, and execution. It makes callback chain mutations and invocations observable.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(notifier_info)` captures callback pointer, priority, and return value. Derived events are `notifier_register`, `notifier_unregister`, and `notifier_run`.

Control flow: Notifier infrastructure emits register/unregister events when blocks are added or removed from a chain, and run events as callbacks are invoked. Function pointers are printed symbolically where possible.

State and persistence: No state is owned. Runtime state remains in caller-owned `struct notifier_block` lists, usually protected by the notifier chain type's lock or SRCU.

Dependencies and integration points: Depends on tracepoints and integrates with atomic/blocking/raw/SRCU notifier chains across PM, netdev, CPU hotplug, reboot, and driver subsystems.

Risks and test signals: Risks include tracing callback pointers after module unload, missing chain identity in the record, and overhead in hot notifier chains. Test register/unregister/run for blocking and atomic chains, module unload, priority ordering, and callback return aggregation.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/notifier.h` completely for this pass (69 lines, 1091 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/notifier.h_research.md`.

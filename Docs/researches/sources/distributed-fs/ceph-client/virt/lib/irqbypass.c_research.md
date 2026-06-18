# sources/distributed-fs/ceph-client/virt/lib/irqbypass.c

## Purpose
This file implements the IRQ bypass manager, a small registry that matches interrupt producers and consumers by shared `eventfd_ctx` so hardware-assisted interrupt delivery can bypass or offload host interrupt paths. Examples include posted interrupts and ARM IRQ forwarding.

## Important APIs, Types, And Functions
Global xarrays `producers` and `consumers` are keyed by the eventfd pointer and protected by a global mutex. `irq_bypass_register_producer()` inserts a producer and connects it to an existing matching consumer. `irq_bypass_unregister_producer()` disconnects and removes it. `irq_bypass_register_consumer()` validates required callbacks, inserts a consumer, and connects to an existing producer. `irq_bypass_unregister_consumer()` disconnects and removes it. Internal `__connect()` and `__disconnect()` sequence optional stop/start callbacks around producer/consumer add and delete callbacks.

## Control Flow And State
Registering either side checks that it is not already registered, inserts it into the matching xarray, then looks for the opposite endpoint with the same eventfd. Connect stops both endpoints, asks the producer to add the consumer if supported, asks the consumer to add the producer, rolls back producer state on failure, restarts both endpoints, and records bidirectional pointers. Disconnect stops both, calls mandatory consumer delete and optional producer delete, restarts both, and clears the pointers.

## Dependencies And Integration Points
The manager depends on `linux/irqbypass.h`, eventfd identity, xarray, mutexes, and module exports. Producers are typically physical interrupt sources such as VFIO devices; consumers are typically KVM irqfd or architecture interrupt injection endpoints.

## Risks And Test Signals
Risks include callback ordering regressions, leaked xarray entries on connection failure, duplicate registration, unregister after failed registration, and deadlocks if callbacks reenter the manager while the mutex is held. Tests should register producer-first and consumer-first, force callback failures, unregister connected and unconnected endpoints, verify stop/start balancing, and run module unload/refcount scenarios.

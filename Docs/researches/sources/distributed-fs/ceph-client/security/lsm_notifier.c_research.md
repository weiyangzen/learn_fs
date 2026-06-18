<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_notifier.c -->
# sources/distributed-fs/ceph-client/security/lsm_notifier.c

## Purpose

`lsm_notifier.c` implements a blocking notifier chain for LSM lifecycle events. It lets kernel code register for events such as all enabled LSMs completing startup.

## Important APIs, Types, and Functions

- `blocking_lsm_notifier_chain` is the global blocking notifier head.
- `call_blocking_lsm_notifier()` dispatches an `enum lsm_event` and data pointer to registered listeners.
- `register_blocking_lsm_notifier()` registers a listener.
- `unregister_blocking_lsm_notifier()` unregisters a listener.

## Control Flow

Callers register a `struct notifier_block`. Event producers call `call_blocking_lsm_notifier()`, which invokes `blocking_notifier_call_chain()`. `lsm_init.c` calls this at late init with `LSM_STARTED_ALL`.

## State and Persistence Behavior

The notifier chain stores registered callbacks for the lifetime of their registration. Because it is a blocking chain, callbacks may sleep but event producers must call it from contexts that permit sleeping.

## Dependencies and Integration Points

The file depends on the kernel notifier API and `<linux/security.h>` for event definitions. It exports all three functions for use outside the core security directory.

## Risks and Edge Cases

Listeners must unregister before their storage disappears. Slow callbacks can delay event delivery. Event data is untyped `void *`, so producers and consumers must agree on semantics for each `enum lsm_event`.

## Test Signals

Tests can register a temporary notifier, trigger or simulate `LSM_STARTED_ALL`, verify call order and return propagation, and validate unregister prevents later invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm_notifier.c -->

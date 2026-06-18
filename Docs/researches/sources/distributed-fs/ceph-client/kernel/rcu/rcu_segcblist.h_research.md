# sources/distributed-fs/ceph-client/kernel/rcu/rcu_segcblist.h

## Purpose
`rcu_segcblist.h` is the internal declaration and inline-helper header for RCU callback list management. It wraps public `linux/rcu_segcblist.h` definitions with helpers used by RCU implementation files.

## Important APIs, types, and functions
The header exposes `rcu_cblist_n_cbs()`, `rcu_segcblist_empty()`, `rcu_segcblist_n_cbs()`, flag helpers, `rcu_segcblist_is_enabled()`, `rcu_segcblist_is_offloaded()`, `rcu_segcblist_restempty()`, and `rcu_segcblist_segempty()`, plus prototypes for all simple-list and segmented-list operations implemented in `rcu_segcblist.c`.

## Control flow
Callers use inline predicates before posting, advancing, extracting, or invoking callbacks. `rcu_segcblist_ready_cbs()` and `rcu_segcblist_pend_cbs()` are implemented in the C file, while these inline helpers provide low-level emptiness and flag decisions. `rcu_segcblist_n_cbs()` chooses atomic or plain reads depending on NOCB support.

## State and persistence behavior
No state is owned by the header. It defines how to read `struct rcu_cblist` and `struct rcu_segcblist` fields safely enough for RCU internals. A key documented behavior is that `head == NULL` does not always mean there are no callbacks, because invocation may temporarily extract callbacks while length accounting remains authoritative.

## Dependencies and integration points
It depends on `linux/rcu_segcblist.h`, RCU segment constants, `CONFIG_RCU_NOCB_CPU`, and flags such as `SEGCBLIST_ENABLED` and `SEGCBLIST_OFFLOADED`. It is included by RCU callback handling code, tree/tiny/SRCU/tasks implementations where segmented lists are enabled, and tests/torture indirectly.

## Risks and invariants
Emptiness helpers must match the tail-pointer representation exactly. Misreading `head` instead of `len` can break barrier or invocation logic. Offload detection must remain conditional on NOCB support. Flag helpers use `WRITE_ONCE()`/`READ_ONCE()` and should not be replaced with plain operations in lockless paths.

## Test signals
Build coverage with and without `CONFIG_RCU_NOCB_CPU`, callback enqueue/invoke torture, CPU offload/deoffload tests, and barrier tests that validate length-based callback detection are the main signals.

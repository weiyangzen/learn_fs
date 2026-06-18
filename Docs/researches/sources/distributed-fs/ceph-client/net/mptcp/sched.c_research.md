# sources/distributed-fs/ceph-client/net/mptcp/sched.c

## Purpose

`sched.c` provides the MPTCP packet scheduler registry and the default scheduler implementation. Schedulers choose which subflow or subflows should transmit new data or retransmitted data by marking `mptcp_subflow_context::scheduled`.

## Important APIs, types, and functions

- `mptcp_sched_default`: built-in scheduler named `default`.
- `mptcp_sched_find()`: RCU lookup by scheduler name.
- `mptcp_get_available_schedulers()`: builds a space-separated scheduler list for sysctl or diagnostics.
- `mptcp_validate_scheduler()`, `mptcp_register_scheduler()`, `mptcp_unregister_scheduler()`: registry lifecycle.
- `mptcp_sched_init()`: registers the default scheduler.
- `mptcp_init_sched()` and `mptcp_release_sched()`: per-socket scheduler selection and module/BPF ref handling.
- `mptcp_sched_get_send()` and `mptcp_sched_get_retrans()`: invoked by the core send and retransmit paths.

## Control flow

At initialization, the default scheduler is registered in the global RCU list. Per MPTCP socket, `mptcp_init_sched()` selects a scheduler by name or falls back to default, takes the module/BPF reference, stores it on `msk->sched`, and calls optional `init`. Send and retransmit paths first respect any already scheduled subflow; otherwise they delegate to fallback handling, the default scheduler, or custom scheduler callbacks. The default scheduler calls `mptcp_subflow_get_send()` or `mptcp_subflow_get_retrans()` from `protocol.c` and marks the returned subflow scheduled.

## State and persistence

Global state is `mptcp_sched_list`, protected by `mptcp_sched_list_lock` for updates and traversed under RCU for reads. Per-socket state is just the selected `msk->sched` pointer and optional scheduler-private state created by callbacks. Per-subflow scheduled state is a boolean in `mptcp_subflow_context`.

## Dependencies and integration points

The registry uses kernel list, RCU, spinlock, module ownership, and BPF module ref helpers. It depends on protocol helpers for selecting default send/retransmit subflows and on `protocol.h` for `struct mptcp_sched_ops` and subflow context access. Core sending in `protocol.c` consumes the scheduled bits set here.

## Risks and edge cases

Schedulers must implement `get_send`; `get_retrans` is optional and falls back to `get_send`. Fallback sockets bypass custom schedulers and only use the first TCP subflow if it can send and has memory. Scheduled bits must be cleared by callers after use; stale scheduled bits can misdirect later sends. Registry updates require RCU safety, and unregistering the default scheduler is intentionally ignored.

## Test signals

Tests should verify scheduler registration, duplicate-name rejection, available scheduler listing, default send/retransmit selection, custom scheduler fallback behavior, module ref release, and behavior during TCP fallback. Packet distribution across subflows and retransmission selection in MPTCP selftests or scheduler-specific tests provide the strongest runtime signal.

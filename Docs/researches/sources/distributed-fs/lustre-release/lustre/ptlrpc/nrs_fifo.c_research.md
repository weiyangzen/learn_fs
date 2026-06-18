# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_fifo.c

## Purpose

`nrs_fifo.c` implements the FIFO NRS policy, the default and fallback scheduler for PTLRPC requests. It preserves the historical non-NRS behavior by serving requests in network arrival enqueue order.

## Important APIs, Types, and Functions

The policy uses `struct nrs_fifo_head`, which contains the FIFO list, embedded resource, and debug sequence counter. Main hooks are `nrs_fifo_start`, `nrs_fifo_stop`, `nrs_fifo_res_get`, `nrs_fifo_req_get`, `nrs_fifo_req_add`, `nrs_fifo_req_del`, and `nrs_fifo_req_stop`. The exported policy configuration is `nrs_conf_fifo`, with name `fifo`, compatibility for all services, and flags `PTLRPC_NRS_FL_FALLBACK | PTLRPC_NRS_FL_REG_START`.

## Control Flow

Policy start allocates and initializes the list head. Resource acquisition is one-level and always returns the embedded FIFO resource. Enqueue assigns a monotonically increasing debug sequence and appends the request to the tail of the list. Dispatch returns the first list entry and removes it unless the caller is only peeking. Dequeue removes an arbitrary queued request from the list. Request stop only logs completion with the stored sequence.

Because FIFO is both fallback and auto-started at registration time, NRS core always has a policy that should accept requests when primary policies reject, are stopped, or do not support the request type.

## State and Persistence Behavior

FIFO state is fully in-memory per NRS head. The list contains currently queued requests, and `fh_sequence` is only for tracing. There is no runtime debugfs configuration and no persistent state.

## Dependencies and Integration Points

FIFO depends on NRS core policy hooks, Linux list primitives, Lustre CPT allocation helpers, request peer formatting, and PTLRPC trace logging. It integrates with every PTLRPC service as the regular and HP fallback policy.

## Risks and Edge Cases

This policy deliberately provides no fairness beyond arrival order, so one client or request class can dominate when FIFO is the only active policy. It must remain reliable because NRS core assumes at least fallback enqueue succeeds. Stop asserts the queue is empty, so lifecycle bugs in core or callers show up as assertions. Sequence wrap is possible over very long lifetimes but affects only debug output.

## Test Signals

Tests should verify tail enqueue/head dequeue order, peek without removal, arbitrary dequeue, sequence assignment, empty queue returning NULL, stop requiring an empty list, fallback auto-start during service setup, and fallback handling when a primary policy rejects a request.

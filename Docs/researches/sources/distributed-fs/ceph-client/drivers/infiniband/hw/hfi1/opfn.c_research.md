# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opfn.c

## Purpose
`opfn.c` implements Omni-Path Feature Negotiation for HFI1 RC QPs. OPFN uses a reserved BTH extended bit plus an atomic compare-swap-shaped work request to exchange feature parameters between peers, currently for TID RDMA.

## Important APIs, types, and functions
- `struct hfi1_opfn_type` maps a feature code to request, response, reply, and error callbacks.
- `hfi1_opfn_handlers[]` currently registers TID RDMA callbacks: `tid_rdma_conn_req`, `tid_rdma_conn_resp`, `tid_rdma_conn_reply`, and `tid_rdma_conn_error`.
- `opfn_conn_request()` chooses the next requested-but-not-completed feature, asks its handler for local data, posts an `IB_WR_OPFN` atomic work request to `HFI1_VERBS_E_ATOMIC_VADDR`, and marks the feature in progress.
- `opfn_conn_response()` handles an incoming OPFN request and builds atomic response data.
- `opfn_conn_reply()` processes the response to a locally posted OPFN request.
- `opfn_conn_error()` clears negotiated state and calls feature error hooks when the QP enters error.
- `opfn_qp_init()` initializes or requests negotiation on RC QP attribute changes, especially RTS transitions with supported MTU.
- `opfn_trigger_conn_request()` sees the BTH extended bit on incoming traffic and starts negotiation if enabled.
- `opfn_init()` and `opfn_exit()` manage the high-priority OPFN workqueue.

## Control flow
QP modification calls `opfn_qp_init()`. For RC QPs with TID RDMA capability and 4K or 8K path MTU, it initializes local TID RDMA OPFN data and sets the requested bit when the QP transitions to RTS. Negotiation starts only after the peer advertises the OPFN extended bit in BTH1; `opfn_trigger_conn_request()` records that support and either calls `opfn_conn_request()` directly or queued work schedules it.

`opfn_conn_request()` runs under the per-QP OPFN spinlock until it needs to call `ib_post_send()`, then drops the lock to avoid QP lock recursion. Responses and replies validate the feature code in the low nibble, call the feature-specific handler, update `completed`, clear `curr`, and report errors to feature handlers when renegotiation or QP error invalidates previous state.

## State and persistence
Per-QP state lives in `struct hfi1_opfn_data`: peer extended-bit support, requested feature bitmask, completed feature bitmask, current in-progress feature, lock, and work item. TID RDMA parameter state lives in QP private data owned by the TID RDMA code. OPFN state is runtime-only and reset on QP error or unsupported MTU transitions.

## Dependencies and integration points
The file integrates with rdmavt QPs and ACK entries, HFI1 QP private data, RDMA work requests, TID RDMA negotiation callbacks, HFI1 capability bits, tracepoints, and a dedicated workqueue used to avoid posting sends while holding QP locks.

## Risks
- OPFN uses a reserved/extended protocol encoding; both peers and the RC path must agree on BTH bit and atomic-address semantics.
- Posting sends while managing QP locks is subtle; queued work avoids a known double-lock path, but direct calls still need caller context awareness.
- Feature bitmask math assumes feature codes start at one and fit in 16-bit masks.
- If `ib_post_send()` fails, the code clears `curr` and reschedules; repeated failure can spin work unless the underlying condition changes.
- Renegotiation clears completed state and invokes feature error callbacks; TID RDMA users must tolerate that transition.

## Test signals
- RC QP tests should cover RTS transition, unsupported MTU clearing, peer extended-bit detection, and successful TID RDMA negotiation.
- Inject invalid feature codes, missing handlers, handler refusal, and `ib_post_send()` failure.
- Force QP error during in-progress and completed negotiation and verify TID RDMA error callbacks and bitmasks reset.
- Concurrency tests should exercise simultaneous incoming OPFN trigger and local QP attribute changes under lockdep.

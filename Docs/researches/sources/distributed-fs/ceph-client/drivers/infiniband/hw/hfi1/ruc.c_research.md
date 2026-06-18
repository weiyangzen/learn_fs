# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ruc.c

## Purpose
`ruc.c` contains shared reliable/unreliable connected transport helpers for HFI1 verbs. It validates inbound connected-transport headers, builds common 9B/16B LRH/OPA/BTH/GRH packet headers for RC and UC send paths, manages SDMA AHG header reuse, and implements the generic QP send loop used by RC, UC, and UD send builders.

## Important APIs, Types, and Functions
- `hfi1_ruc_check_hdr()` validates received packet addressing against the QP path or alternate path, including migration bit, GRH presence and GID matching, P_Key checks, SLID, port number, and migration state transitions.
- `hfi1_make_grh()` constructs an InfiniBand GRH from an RDMA global route.
- `build_ahg()` allocates or reuses an SDMA AHG entry for repeated middle packets and emits AHG update descriptors for PSN changes.
- `hfi1_make_ruc_header_9B()` and `hfi1_make_ruc_header_16B()` build local route headers and BTH fields for 9B and 16B packet formats.
- `hfi1_make_ruc_header()` resets per-packet AHG metadata and dispatches to the selected header builder.
- `hfi1_schedule_send_yield()` enforces a send-loop time slice and reschedules RC or TID send work when a QP has run too long.
- `hfi1_do_send()`, `_hfi1_do_send()`, and `hfi1_do_send_from_rvt()` are send engine entry points.

## Control Flow
Receive-side validation uses `hfi1_ruc_check_hdr()` before RC and UC packet processing. If a QP is armed for migration and the packet carries the migrated path bit, the function validates alternate path GRH/GID/P_Key/SLID data and then calls `hfi1_migrate_qp()` under `s_lock`. Otherwise it validates the primary remote path and rearms migration when appropriate.

Transmit header construction starts with the opcode-specific builder in `rc.c`, `uc.c`, `tid_rdma.c`, or `ud.c`, which fills BTH fields and payload length in `hfi1_pkt_state`. `hfi1_make_ruc_header()` clears stale AHG fields in the QP private AHG tx request and calls the 9B or 16B builder. The builder adds GRH when needed, applies migration and ECN/BECN bits, computes padding and length fields, applies the P_Key, optionally uses AHG for middle packets, and writes either IB LRH or OPA 16B headers.

The send loop in `hfi1_do_send()` chooses `hfi1_make_rc_req()`, `hfi1_make_uc_req()`, or `hfi1_make_ud_req()` by QP type. It handles local loopback, takes `s_lock`, checks `hfi1_send_ok()`, marks the QP busy, sends any waiting prebuilt txreq through `hfi1_verbs_send()`, calls the selected make-request function until it cannot build more, and uses `hfi1_schedule_send_yield()` to avoid monopolizing CPU/workqueue time.

## State and Persistence Behavior
The file manipulates runtime QP and QP-private state: migration state, AHG index/valid flags, AHG update counts, send busy flags, iowait pending flags, packet timeout bookkeeping, and selected SDMA engine CPU. It does not persist data beyond in-memory driver structures. AHG entries are allocated from and freed to the selected SDMA engine, so stale AHG flags must be cleared for packets that cannot safely use a copied header.

## Dependencies and Integration Points
`ruc.c` integrates with RDMA address handles, HFI1 P_Key/GID/LID/SL/SC helpers, SDMA AHG APIs from `sdma.h`, verbs tx request allocation and send, RC/UC/UD packet builders, TID RDMA send scheduling, and RDMA VT loopback support. It is a common layer for RC and UC receive validation and all connected transmit header formatting.

## Risks and Edge Cases
Header format differences are a major risk: 9B versus 16B padding, GRH placement, multicast GRH handling, BECN bit placement, path bits, permissive LID behavior, and P_Key placement must remain exact. AHG must be disabled when GRH, migration, or ECN changes make a copied header unsafe. Send-loop locking must keep one CPU from sending a QP out of order. Migration validation must not accept mismatched GIDs or SLIDs, and P_Key failures must update bad-P_Key reporting without advancing protocol state.

## Test Signals
Useful tests include RC and UC traffic over 9B and 16B headers, GRH and non-GRH paths, multicast 16B GRH behavior, path migration, bad P_Key and bad SLID rejection, ECN/BECN propagation, AHG-enabled large SEND/RDMA WRITE middle packet streams, loopback QPs, and send-loop fairness under heavy QP fan-out. Tracepoints for send scheduling and AHG allocation are useful diagnostics.

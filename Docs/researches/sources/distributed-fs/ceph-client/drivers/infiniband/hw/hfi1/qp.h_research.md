# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qp.h

## Purpose
`qp.h` declares HFI1-specific QP flags, scheduling helpers, resource mapping APIs, lifecycle callbacks supplied to RDMAVT, and inline helpers used by send paths.

## Important APIs, Types, And Functions
The header reserves high `s_flags` bits for AHG validity/clear, PIO drain wait, TID space/response wait, and send halt. `hfi1_send_ok()` decides if send progress can run based on busy and wait flags plus pending queued work or response state. `clear_ahg()` resets AHG state and frees the SDMA AHG index. Declarations cover QP wakeup, SDMA/send-context mapping, scheduling, migration, private allocation/free, MTU conversion, waiter flushing, error notification, quiesce, port-QP erroring, and unbusy handling.

## Control Flow
Send paths consult `hfi1_send_ok()` before scheduling, set wait flags when PIO/SDMA/TID resources are unavailable, and later call `hfi1_qp_wakeup()` or `hfi1_qp_unbusy()` to resume progress. RDMAVT calls the declared hooks for QP creation, modification support, reset, error, and teardown.

## State And Persistence
The header defines bit assignments stored in `rvt_qp::s_flags` and manipulates AHG state in `hfi1_qp_priv`. These are runtime QP state only. The `HFI1_S_MIN_BIT_MASK` documents the boundary below which the base RDMAVT layer owns flags.

## Dependencies And Integration Points
It includes RDMAVT QP definitions, HFI1 verbs, SDMA, and verbs txreq headers. It is shared by QP implementation, PIO code, SDMA send paths, TID RDMA, and other verbs code that needs HFI1 wait semantics.

## Risks
Flag-bit collisions with RDMAVT would corrupt send state, so additions must stay above the documented minimum. `clear_ahg()` assumes `priv->s_ahg` exists and that SDMA AHG free is safe when `s_sde` is set and index is nonnegative. Inline scheduling predicates must remain consistent with wakeup paths.

## Test Signals
Compile coverage for flag users, AHG allocation/free cycles, send scheduling under each wait flag, TID wait interactions, and static checks that HFI1 flags do not overlap RDMAVT-defined bits.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/tx.c

## Purpose
`libeth/tx.c` provides base Tx completion for normal and XDP SQEs, with optional XDP/XSk completion targets patched in by the XDP module.

## Important APIs, Types, and Functions
`libeth_tx_complete_any()` completes either normal SQEs or XDP SQEs. `libeth_attach_xdp()` updates static-call targets for XDP bulk returns and XSk buffer frees. Two `DEFINE_STATIC_CALL_NULL` entries hold optional callbacks.

## Control Flow
Completion checks `sqe->type`: XDP types go through `__libeth_xdp_complete_tx()` with current static-call targets; normal entries call `libeth_tx_complete()`. Attach updates both static calls to XDP ops or null.

## State and Persistence Behavior
Static-call target state persists module-wide and changes when `libeth_xdp` loads/unloads. SQE state is consumed by completion helpers owned by public libeth headers.

## Dependencies and Integration Points
Depends on `net/libeth/xdp.h` and private attach declarations. It is the base module side of the optional XDP module split.

## Risks and Edge Cases
If `libeth_xdp` is absent, XDP SQEs cannot be fully handled; the comment explicitly notes this. Attach/detach ordering must avoid stale function targets during module unload.

## Test Signals
Tx completion with normal SQEs, XDP SQEs before/after XDP module load, module unload cleanup, and static-call target updates under modular builds.

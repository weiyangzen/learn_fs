# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/priv.h

## Purpose
`priv.h` is the private bridge between base `libeth` and `libeth_xdp`. It declares XDP/XSk slowpath helpers and a small operation table used to attach/detach optional XDP support to base Tx completion.

## Important APIs, Types, and Functions
It declares `libeth_xsktmo_slow`, XSk return/exception helpers, `struct libeth_xdp_ops`, `libeth_attach_xdp()`, and inline `libeth_detach_xdp()`.

## Control Flow
At `libeth_xdp` module init, `xdp.c` calls `libeth_attach_xdp(&xdp_ops)` to update base static calls. At exit it calls `libeth_detach_xdp()`, passing null ops.

## State and Persistence Behavior
No direct state in the header. It exposes the attach API that mutates static-call targets in `tx.c`.

## Dependencies and Integration Points
Used by `tx.c`, `xdp.c`, and `xsk.c`. It intentionally avoids exposing these internals as public kernel API while allowing separate module composition.

## Risks and Edge Cases
The operations must remain valid for the lifetime of `libeth_xdp`; detach must happen before code unload. Signature drift between private declarations and XDP implementations would break builds.

## Test Signals
Module load/unload of `libeth_xdp`, base Tx completion with XDP module absent, and consumer cleanup of XDP SQEs while XDP support is present.

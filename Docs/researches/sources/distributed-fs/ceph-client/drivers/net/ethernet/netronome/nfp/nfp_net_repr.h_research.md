# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_repr.h

## Purpose

`nfp_net_repr.h` declares the representor data structures and APIs used by NFP applications and port-management code. It defines representor containers, per-CPU stats, representor private data, representor type IDs, and helpers to identify and allocate NFP representor netdevs.

## Important APIs, Types, and Functions

Important types are `struct nfp_reprs`, `struct nfp_repr_pcpu_stats`, `struct nfp_repr`, and `enum nfp_repr_type`. Important helpers are `nfp_netdev_is_nfp_repr()`, `nfp_repr_get_port_id()`, and `nfp_repr_alloc()`. Declared functions cover locked lookup, RX stats increment, feature transfer, initialization/free, multi-queue allocation, clean-and-free, cleanup by type, representor set allocation, and physical-port resync.

## Control Flow

The header supports representor lifecycle flows: allocate a netdev with `nfp_repr_alloc_mqs()`, initialize it against an app, control-message port ID, NFP port, and lower PF netdev via `nfp_repr_init()`, use `nfp_repr_netdev_ops` for runtime callbacks, then clean/free individual representors or entire RCU-protected sets during app shutdown or port invalidation.

## State and Persistence Behavior

The structures persist mapping between Linux representor netdevs, firmware port IDs, app state, port state, and per-CPU packet counters. `reprs[]` is RCU-protected because datapath/control paths may look up representors while app code replaces or removes sets.

## Dependencies and Integration Points

The header depends on `net/dst_metadata.h`, net_device APIs, u64 stats sync, NFP app/port forward declarations, and the implementation in `nfp_net_repr.c`. It is used by application modules, SR-IOV representor management, port refresh, and packet receive paths that need to account CPU hits.

## Risks and Edge Cases

`nfp_repr_get_port_id()` assumes the netdev is an initialized NFP representor with a metadata dst. Callers must use the locked/RCU lookup contracts for `struct nfp_reprs`. Per-CPU stat comments include a typo around `tx_bytes`, but fields are clear. Representor type bounds depend on `NFP_REPR_TYPE_MAX`.

## Test Signals

Compile all representor consumers, validate type-based cleanup, RCU lookup under concurrent removal, port-ID extraction, and stats accounting. Static analysis should check callers do not pass plain NFP netdevs to representor-only helpers.

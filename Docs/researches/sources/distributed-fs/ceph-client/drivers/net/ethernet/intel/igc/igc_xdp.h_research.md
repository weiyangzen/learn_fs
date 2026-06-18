# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_xdp.h

## Purpose
`igc_xdp.h` declares the IGC XDP and AF_XDP setup interface and provides a small inline predicate for XDP-enabled adapter state.

## Important APIs, Types, and Functions
The header declares `igc_xdp_set_prog()` for BPF program attach/detach and `igc_xdp_setup_pool()` for AF_XDP pool enable/disable by queue. `igc_xdp_is_enabled()` returns whether `adapter->xdp_prog` is non-NULL.

## Control Flow
There is no complex control flow. The inline helper is a boolean pointer check used by pool setup and other driver paths to decide whether XDP-specific queue handling is active.

## State and Persistence Behavior
The header owns no state. It reads `adapter->xdp_prog`, which is runtime-only and managed by `igc_xdp.c`.

## Dependencies and Integration Points
It depends on declarations for `struct igc_adapter`, `struct bpf_prog`, `struct netlink_ext_ack`, and `struct xsk_buff_pool` from including headers. It is included by IGC control paths that need to attach XDP programs or configure AF_XDP zero-copy pools.

## Risks and Edge Cases
The predicate reports only attached BPF program state, not AF_XDP pool state. Callers that need zero-copy state must inspect ring flags or pool bindings separately.

## Test Signals
Compile all callers, verify attach/detach paths use the declarations correctly, and ensure callers do not treat `igc_xdp_is_enabled()` as an AF_XDP pool predicate.

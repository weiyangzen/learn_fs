# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_xdp.h

## Purpose
Declares bnxt XDP entry points and the small wrapper context used for XDP RX hash metadata extraction.

## Important APIs, Types, And Functions
`struct bnxt_xdp_buff` embeds `struct xdp_buff` and carries RX completion pointers plus completion type so `bnxt_xdp_rx_hash()` can derive RSS hash metadata. The header declares XDP TX descriptor construction, TX completion, RX execution, program setup, ndo xmit, attach checks, buffer initialization, fragment cleanup, skb fragment finalization, and RX hash metadata functions. It also declares `bnxt_xdp_locking_key`.

## Control Flow
The header has no runtime control flow. It provides declarations consumed by core RX/TX and netdev setup code so XDP-specific behavior can be called from the main datapath.

## State And Persistence Behavior
The header defines transient per-packet context (`bnxt_xdp_buff`) and references external static-branch state. Persistent XDP program and ring state are owned by `struct bnxt` and ring structures in the implementation.

## Dependencies And Integration Points
It integrates XDP support with bnxt RX completion code, TX ring cleanup, netdev BPF setup, page-pool-backed RX buffers, and BPF metadata helpers. It depends on bnxt ring types and Linux XDP types.

## Risks
`struct bnxt_xdp_buff` must remain layout-compatible with casting from `const struct xdp_md *` in `bnxt_xdp_rx_hash()`, with the embedded `xdp_buff` first. Prototype changes must stay synchronized with call sites in the RX/TX datapath.

## Test Signals
Compile coverage plus runtime XDP attach, RX action, TX completion, and metadata hash tests from `bnxt_xdp.c` cover this header's contracts.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_xdp.c

## Purpose
Implements XDP support for bnxt RX and TX rings. It attaches/detaches XDP programs, runs programs on received packets, supports `XDP_PASS`, `XDP_DROP`, `XDP_ABORTED`, `XDP_TX`, and `XDP_REDIRECT`, builds XDP TX descriptors including fragments, handles XDP TX completions and page recycling, exposes ndo XDP xmit, builds skb fragment metadata after XDP pass, and implements XDP RX hash kfunc support.

## Important APIs, Types, And Functions
The public functions are `bnxt_xdp()`, `bnxt_rx_xdp()`, `bnxt_xdp_xmit()`, `bnxt_tx_int_xdp()`, `bnxt_xmit_bd()`, `bnxt_xdp_attached()`, `bnxt_xdp_buff_init()`, `bnxt_xdp_buff_frags_free()`, `bnxt_xdp_build_skb()`, and `bnxt_xdp_rx_hash()`. `bnxt_xdp_locking_key` is a static branch used to enable XDP TX locking when needed. `bnxt_xmit_bd()` is the shared descriptor builder for XDP_TX and XDP_REDIRECT paths.

## Control Flow
Program setup enters through `bnxt_xdp()` and `bnxt_xdp_set()`. Setup validates MTU versus fragment support, disallows XDP with HDS, requires combined RX/TX channels, checks ring resources, closes the NIC if running, swaps `bp->xdp_prog`, updates skb/page mode and redirect target features, recomputes XDP TX ring counts and ring parameters, and reopens the NIC if needed.

RX processing calls `bnxt_xdp_buff_init()` to sync DMA and prepare an `xdp_buff`, then `bnxt_rx_xdp()` runs the BPF program. PASS returns false so the normal stack path continues. TX checks descriptor availability, syncs DMA for device, queues a TX BD referencing the RX page, marks events for TX completion, and reuses the RX buffer. REDIRECT allocates a replacement RX buffer before `xdp_do_redirect()` and marks redirect events. DROP/ABORTED recycle fragments and reuse RX data. ndo `bnxt_xdp_xmit()` maps external XDP frames, queues redirect descriptors on a CPU-selected XDP TX ring, and optionally flushes the doorbell.

TX completions in `bnxt_tx_int_xdp()` distinguish redirected frames from XDP_TX recycled RX pages. Redirect completions unmap DMA and return the frame; XDP_TX completions recycle fragment pages and ring the RX doorbell when needed.

## State And Persistence Behavior
XDP state is in `bp->xdp_prog`, per-RX-ring `rxr->xdp_prog`, `bp->tx_nr_rings_xdp`, adjusted total TX/CP ring counts, page-pool state, TX software descriptors with `action`, `rx_prod`, `xdpf`, page and DMA metadata, and netdev XDP redirect-target feature flags. No persistent disk state exists. Program references are owned through BPF refcounts and the old program is released after `xchg()`.

## Dependencies And Integration Points
The file integrates with Linux XDP/BPF APIs, page pool recycling, PCI DMA mapping/syncing, bnxt ring macros and doorbells, netdev instance locking, NIC open/close flows, RSS completion formats, and tracepoints for XDP exceptions. It depends on ring sizing helpers from core bnxt code and assumes XDP runs in page mode.

## Risks
DMA ownership and page recycling are the highest-risk areas: XDP_TX reuses RX pages, REDIRECT needs replacement allocation before handoff, and fragmented XDP requires recycling all frags on drop/error. Ring-full behavior must avoid advancing RX producer too early. Program attach must preserve NIC state across close/reopen and reject unsupported MTU/HDS/channel layouts. `bnxt_xdp_xmit()` can run concurrently and only locks when the static key says it is needed.

## Test Signals
Run XDP programs for PASS, DROP, ABORTED, TX, and REDIRECT; include multi-buffer/frags, jumbo MTU with and without frag-capable programs, ring exhaustion, redirect to another device, external ndo xmit, attach/detach while the NIC is up, attach rejection with HDS or split channels, TX completion recycling, DMA mapping failures, and `bpf_xdp_metadata_rx_hash` behavior for L2, IPv4/IPv6, TCP/UDP/ICMP, and v3 completion formats.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_txrx_lib.h

Purpose: declares inline descriptor helpers and shared RX/XDP helper prototypes for the ice datapath. It is included by `ice_txrx.c` and `ice_txrx_lib.c`.

Important APIs and helpers: `ice_test_staterr()` tests little-endian RX descriptor status/error bits. `ice_is_non_eop()` identifies multi-buffer packets and increments `rx_non_eop_descs`. `ice_build_ctob()` builds the transmit data descriptor command/offset/buffer-size/tag quadword. `ice_build_tstamp_desc()` builds a TX time scheduling descriptor. `ice_get_vlan_tci()` extracts a stripped VLAN tag from L2TAG1 or L2TAG2. `ice_xdp_ring_update_tail()` writes the XDP TX tail with a barrier. `ice_set_rs_bit()` sets Report Status on the last produced XDP descriptor and returns its index.

Control flow role: these helpers sit directly in hot paths. TX descriptor construction and XDP RS/tail updates depend on them for correct bit packing and ordering. RX processing uses `ice_is_non_eop()` to defer skb construction until end-of-packet and uses `ice_get_vlan_tci()` before GRO delivery.

State and persistence: inline helpers update descriptor memory, ring statistics, and MMIO tail registers. They do not allocate resources, but the ordering effects are persistent from hardware's perspective because descriptor writes become visible before tail updates.

Dependencies and integration: includes `ice.h` for descriptor and ring definitions, hardware bit masks, and stats helpers. Prototypes expose the C helpers for RX descriptor release, skb metadata processing, skb receive, XDP TX submission, and XDP batch finalization.

Risks: endian and bit-shift mistakes here corrupt hardware descriptors. `ice_set_rs_bit()` assumes `next_to_use` is already advanced and wraps correctly. `ice_get_vlan_tci()` assumes only one stripped tag is supported by the OS/PF configuration. Barriers before tail writes are required on weakly ordered architectures.

Test signals: compile for endian correctness, TX descriptor inspection on real hardware, XDP_TX completion with RS wraparound, VLAN tag extraction for L2TAG1/L2TAG2, multi-buffer RX packets, and refill tail-write behavior.

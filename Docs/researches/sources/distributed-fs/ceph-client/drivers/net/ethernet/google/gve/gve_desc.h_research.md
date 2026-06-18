# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_desc.h

## Purpose

`gve_desc.h` defines the legacy GQI descriptor ABI shared between the host driver and the Google virtual NIC. It contains packed TX packet, metadata, and segment descriptors, RX completion/data-slot descriptors, descriptor flags, IRQ doorbell bits, and small helpers for RX RSS and sequence tracking.

## Important APIs, types, and constants

- `struct gve_tx_pkt_desc`, `struct gve_tx_mtd_desc`, `struct gve_tx_seg_desc`: the legacy transmit descriptor variants used through `union gve_tx_desc` in `gve.h`.
- `GVE_TXD_STD`, `GVE_TXD_TSO`, `GVE_TXD_SEG`, `GVE_TXD_MTD`: descriptor type encodings placed in the upper bits of `type_flags`.
- `GVE_TXF_L4CSUM`, `GVE_TXF_TSTAMP`, `GVE_TXSF_IPV6`: TX offload flags.
- Path metadata constants such as `GVE_MTD_PATH_STATE_*` and `GVE_MTD_PATH_HASH_L4`: used by `gve_tx_fill_mtd_desc()` when an SKB has an L4 hash.
- `struct gve_rx_desc`: a 64-byte RX packet descriptor with RSS hash, checksum, length, header offsets, flags, and 3-bit sequence number.
- `union gve_rx_data_slot`: describes either a raw DMA address or a QPL offset.
- `GVE_RX_PAD`: two-byte RX packet alignment pad consumed by `gve_rx.c`.
- `GVE_RXF_*`, `GVE_SEQNO()`, `gve_next_seqno()`: RX validation and packet classification helpers.
- `GVE_IRQ_ACK`, `GVE_IRQ_MASK`, `GVE_IRQ_EVENT`: legacy interrupt doorbell bits.

## Control flow and state

This header has no runtime state, but it fixes the wire layout expected by `gve_tx.c` and `gve_rx.c`. TX code writes descriptors in host memory, performs any DMA sync/mapping, increments `tx->req`, and rings the legacy doorbell. RX code reads `flags_seq`, validates sequence progression using `gve_next_seqno()`, interprets packet-continuation/error bits, and uses `gve_needs_rss()` to decide when to apply RSS hash metadata.

## Dependencies and integration points

The file depends on Linux endian helpers and `static_assert`/`BIT`. It is included by `gve.h`, which embeds the descriptor structures in ring state. `gve_tx.c` fills the TX variants; `gve_rx.c` parses RX descriptors; `gve_main.c` uses IRQ bits while masking/acking legacy GQI interrupts.

## Risks and test signals

Risks are ABI drift against NIC firmware, endian mistakes, changing packed layouts, and misinterpreting sequence/continuation bits under multi-fragment RX. Tests should cover descriptor size assertions, GQI TX checksum/TSO metadata, RX sequence wrap from 7 to 1, fragmented RX assembly, and both QPL-offset and raw-DMA data-slot modes.

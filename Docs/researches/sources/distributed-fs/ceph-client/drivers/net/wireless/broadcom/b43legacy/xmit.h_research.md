# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/xmit.h

## Purpose
Defines b43legacy firmware v3 TX/RX descriptor layouts, PLCP header structures, TX/RX status bitfields, QoS constants, and TX/RX helper prototypes.

## Important APIs, Types, and Functions
Key types are `struct b43legacy_plcp_hdr4`, `struct b43legacy_plcp_hdr6`, `struct b43legacy_txhdr_fw3`, `struct b43legacy_txstatus`, `struct b43legacy_hwtxstatus`, and `struct b43legacy_rxhdr_fw3`. The header defines `B43legacy_TX4_MAC_*`, `B43legacy_TX4_PHY_*`, `B43legacy_RX_PHYST*`, `B43legacy_RX_MAC_*`, `B43legacy_RX_CHAN_*`, TX suppression reasons, and inline key-index translators `b43legacy_kidx_to_fw()`/`b43legacy_kidx_to_raw()`.

## Control Flow, State, and Persistence
No executable control except key-index inline helpers. The structs describe packed firmware-facing state carried in device queues and RX/TX status rings; incorrect layout directly changes hardware protocol interpretation.

## Dependencies and Integration Points
Includes `main.h` and is consumed by `xmit.c`, PIO, DMA, and status handling. The key-index helpers depend on firmware revision and driver key-table layout.

## Risks and Test Signals
Packed layout and bitfield risks are high: size/alignment drift breaks firmware communication. Test compile with structure users, TX/RX traffic, encrypted traffic on old and newer firmware key-index APIs, and TX-status decoding.

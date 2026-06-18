# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/xmit.h

## Purpose
Defines the modern `b43` transmit/receive firmware data structures and bitfields consumed by `xmit.c`, DMA, and PIO code. It documents the packed TX header layouts for multiple v4 firmware formats, RX metadata layout, TX status report format, PLCP headers, security key-index conversion helpers, and the driver-private mac80211 TX metadata storage.

## Important APIs, Types, and Functions
Important types are `struct b43_plcp_hdr4`, `struct b43_plcp_hdr6`, `struct b43_txhdr`, `struct b43_tx_legacy_rate_phy_ctl_entry`, `struct b43_txstatus`, `struct b43_rxhdr_fw4`, and `struct b43_private_tx_info`. Important inline helpers are `b43_txhdr_size`, `b43_new_kidx_api`, `b43_kidx_to_fw`, `b43_kidx_to_raw`, and `b43_get_priv_tx_info`. The file exports prototypes for TX header generation, PLCP generation, RX delivery, TX status handling, and TX suspend/resume.

## Control Flow
This header has no runtime control flow beyond inline helpers. Consumers select a TX header size from `dev->fw.hdr_format`, write fields into one of the packed firmware-format union members, and use bit masks to build MAC/PHY control words. RX code reads the packed firmware header and decodes PHY/MAC/channel bitfields into mac80211 status. Key-index helpers convert indexes at the boundary between mac80211-visible raw key slots and firmware-specific key numbering.

## State and Persistence
The declarations describe volatile firmware-facing memory and skb control metadata only. No persistent state exists here. The packed layout is itself a persistence-like ABI contract with the firmware and DMA/PIO descriptor code: padding and field sizes must remain stable.

## Dependencies and Integration Points
Depends on `main.h`, Linux packed integer types, and mac80211. It is used by `xmit.c`, DMA/PIO transmit paths, debugfs TX status logging, and any code that needs to size or decode b43 firmware headers.

## Risks
Packed layout drift can break firmware communication silently. The key-index conversion has a documented uncertainty about the exact revision where the API changed. `b43_txhdr_size` must stay consistent with `struct b43_txhdr` union layouts and supported firmware revisions. Rate and PHY bit definitions must remain aligned with firmware expectations, not merely compiler layout.

## Test Signals
Compile-time structure-size checks, successful TX on firmware formats 351/410/598, key-index correctness with default and per-station keys, and RX metadata sanity across CCK/OFDM/N/HT PHYs are the primary signals. DMA/PIO smoke tests should catch incorrect TX header sizes through failed transmission or bad cookies.

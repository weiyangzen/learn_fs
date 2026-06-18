# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800usb.h

## Purpose
Defines RT2800 USB firmware constants and USB-specific descriptor bitfields. It captures the TXINFO/RXINFO and trailing RXD layout used by `rt2800usb.c`.

## Important APIs, Types, And Functions
Defines `FIRMWARE_RT2870`, USB `FIRMWARE_IMAGE_BASE` (`0x3000`), `TXINFO_DESC_SIZE`, `RXINFO_DESC_SIZE`, `TXINFO_W0_*` fields for packet length, WIV, QSEL, bulk aggregation, and burst flags, `RXINFO_W0_USB_DMA_RX_PKT_LEN`, and `RXD_W0_*` fields for frame classification, CRC/cipher status, AMSDU/AMPDU, L2 padding, decryption, cipher algorithm, last AMSDU, PLCP RSSI, and PLCP signal.

## Control Flow
`rt2800usb_write_tx_desc()` writes TXINFO fields before submitting bulk URBs. `rt2800usb_fill_rxdone()` reads RXINFO at skb start, removes it, locates RXD after `rx_pkt_len`, decodes RX status flags, trims the packet, and passes RXWI to shared RT2800 logic. Firmware constants drive USB firmware upload and module metadata.

## State And Persistence
No direct runtime state is declared. Descriptor constants define the packet ABI between host USB buffers and device DMA engine.

## Dependencies And Integration Points
Depends on rt2x00 bitfield macros. It integrates with `rt2x00usb` queue code, RT2800 RXWI/TXWI parsing, mac80211 RX status flags, and Linux firmware loading.

## Risks
The TXINFO packet length excludes TXINFO itself and must match USB padding rules; incorrect values produce truncated or stuck bulk transfers. RXD is placed after variable-length packet data, so packet length validation is critical before reading. Firmware base differs from PCI and must not be shared.

## Test Signals
USB TX/RX descriptor dumps, RX size corruption tests, hardware crypto status tests, firmware upload using `rt2870.bin`, and bulk transfer stress with packet sizes at 4-byte boundaries.

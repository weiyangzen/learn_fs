# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mac.h

## Purpose
Descriptor bitfield definitions and packet-type enums for MT7603 RX descriptors, RX vector groups, TX descriptors, TX rate encoding, and TX status records.

## Important APIs, Types, And Functions
- `enum rx_pkt_type` classifies hardware RX entries as TX status, RXV, normal RX, duplicate RFB, timing report, retrieve/loopback, or MCU event.
- `MT_RXD*` macros decode normal RX descriptor fields: length/type, optional groups, BSSID, payload/hdr flags, channel index, key ID, unicast/multicast, errors, security mode, TID, and WLAN index.
- `MT_RXV*` macros decode PHY vector fields for mode, rate, SGI, LDPC, STBC, bandwidth, RSSI/RCPI, noise, and validity.
- `enum mt7603_tx_header_format` and `MT_TXD*` macros define TXWI layout, queue/WCID/vif/TID/protection/rate/PN/status fields.
- `MT_TX_RATE_*` macros encode fixed/probed hardware rates.
- `MT_TXS*` macros decode TX status including timeout reasons, ack state, final rate, timestamp, WCID, retry count, AMPDU state, PID, bandwidth, and sequence/TSSI fields.

## Control Flow
Header-only definitions are consumed by `dma.c` and `mac.c`. RX descriptor macros drive packet dispatch and status construction. TX descriptor macros drive `mt7603_mac_write_txwi()`. TX status macros drive rate/status reporting in `mt7603_fill_txs()`.

## State And Persistence
No direct state. It defines the binary contract between host driver memory and MT7603 hardware/firmware descriptors.

## Dependencies And Integration Points
Depends on Linux bitfield macros (`GENMASK`, `BIT`, `FIELD_GET`, `FIELD_PREP`) via included headers. Must stay synchronized with MT7603 hardware documentation and firmware behavior.

## Risks
Wrong bit definitions cause silent RX drops, bad security metadata, incorrect rate/status reporting, DMA queue corruption, or malformed TX descriptors. Some fields overlap or have format-dependent meaning, so consumers must use the correct packet type and optional group checks.

## Test Signals
Descriptor-level validation comes from RX/TX traffic across CCK/OFDM/HT rates, 20/40 MHz, encrypted frames, fragmented CCMP, AMPDU, TX status with retries/timeouts, and MCU event dispatch. Hardware trace dumps should match expected field decodes.

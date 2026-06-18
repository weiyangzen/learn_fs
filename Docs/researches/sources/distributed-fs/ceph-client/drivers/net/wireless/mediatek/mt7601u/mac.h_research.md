# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/mac.h

## Purpose
Defines MT7601U MAC descriptor structures, RX/TX info bitfields, PHY mode enums, TXWI layout, and MAC helper prototypes.

## Important APIs, Types, And Functions
Key structures are `struct mt76_tx_status`, `struct mt7601u_rxwi`, and `struct mt76_txwi`. The header defines `MT_RXINFO_*`, `MT_RXWI_*`, `MT_TXWI_*`, `enum mt76_phy_type`, and `enum mt76_phy_bandwidth`. Prototypes expose RX processing, key programming, rate programming, TX status fetch/report, and MAC address setup.

## Control Flow
No direct control flow. The bitfield definitions drive parsing/creation of hardware RXWI/TXWI/status records in `mac.c`, `dma.c`, and TX code.

## State And Persistence
Structures mirror hardware-visible descriptors and persistent per-WCID/rate/key state. RXWI fields carry RSSI, rate, MPDU length, decrypt status, and control metadata from hardware to driver.

## Dependencies And Integration Points
Used by MT7601U DMA, MAC, TX, and main callback code. Depends on SKB/mac80211 types via included translation units.

## Risks
Packed/aligned layout must match hardware exactly. The comments warn that some RSSI/SNR naming is based on vendor-driver interpretation rather than clean public documentation.

## Test Signals
RXWI parsing yields correct frame lengths/rates/RSSI, TXWI produced by TX code is accepted by hardware, and key/rate helper prototypes match all call sites.

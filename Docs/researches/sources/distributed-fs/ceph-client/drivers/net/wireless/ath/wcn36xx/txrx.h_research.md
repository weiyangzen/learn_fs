# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/txrx.h

## Purpose
`txrx.h` defines WCN36xx firmware RX/TX buffer descriptor layouts, TX queue/rate constants, sequence-number fill policy, and the exported TX/RX helpers used by the DXE and mac80211 glue.

## Important APIs, Types, and Functions
- `struct wcn36xx_pdu` describes common MPDU layout fields embedded in RX and TX descriptors.
- `struct wcn36xx_rx_bd` mirrors the firmware RX descriptor, including status bits, PDU offsets, PHY stats, reorder metadata, channel/band, and A-MSDU flags.
- `struct wcn36xx_tx_bd` mirrors the firmware TX descriptor, including queue, rate, ACK policy, station index, DPU descriptor, and timing fields.
- `enum wcn36xx_txbd_ssn_type` controls whether sequence numbers are filled by host or DPU.
- `wcn36xx_rx_skb()`, `wcn36xx_start_tx()`, and `wcn36xx_process_tx_rate()` are the public functions implemented in `txrx.c`.

## Control Flow
The header does not implement control flow, but its bitfield ordering and descriptor sizes directly drive the TX/RX processing path. `txrx.c` writes these structures, converts them to firmware byte order, and validates their offset fields on receive.

## State and Persistence Behavior
Descriptor instances are transient per-frame objects. Constants such as `WCN36XX_TX_B_WQ_ID`, `WCN36XX_TX_U_WQ_ID`, and `WCN36XX_TID` encode persistent firmware queue contract assumptions.

## Dependencies and Integration Points
It includes Linux Ethernet helpers and `wcn36xx.h`; it references mac80211 skbs and HAL stats types. DXE code consumes the TX descriptor built from these definitions, while RX code receives firmware-populated instances.

## Risks and Test Signals
The risk is high for ABI drift: C bitfield layout must match firmware expectations and is sensitive to compiler/endianness assumptions mitigated by explicit word swapping in callers. Test signals include successful RX/TX across data, management, broadcast, QoS, and encrypted paths plus descriptor dumps that match firmware documentation.

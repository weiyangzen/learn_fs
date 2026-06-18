<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan.h

## Purpose
This header is the central hardware and data-path contract for the WILC1000 driver. It defines register addresses, bit fields, packet header layouts, queue structures, host-interface callbacks, config frame structures, chip-id helpers, and public core function prototypes used by the SDIO, SPI, cfg80211, and netdev layers.

## Important APIs, Types, And Functions
Major definitions include WILC peripheral/VMM/SPI/SDIO/register constants, interrupt status and clear bit fields, TX/RX buffer sizes, packet type IDs, config packet command IDs, VMM header fields, WMM access-category definitions, and chip id base/revision constants. `struct wilc_hif_func` is the bus abstraction consumed by `wlan.c` and implemented by `sdio.c` and `spi.c`.

Important data types are `struct txq_entry_t`, `struct txq_fw_recv_queue_stat`, `struct txq_handle`, `struct rxq_entry_t`, `struct tx_complete_data`, `struct wilc_cfg_cmd_hdr`, `struct wilc_cfg_frame`, and `struct wilc_cfg_rsp`. Inline helpers `is_wilc1000()` and `is_wilc3000()` classify chip ids after masking revision bits.

## Control Flow
The header does not execute control flow directly, but it shapes the common paths. Bus drivers populate `struct wilc_hif_func`; `wlan.c` calls those callbacks for initialization, register I/O, block I/O, interrupt processing, VMM selection, and reset. TX queue entries carry packet type, queue number, payload buffer, callback, private data, VIF, and TCP ACK bookkeeping into `wilc_wlan_handle_txq()`. Config frame structures define how WID set/get operations are wrapped before being queued as `WILC_CFG_PKT`.

## State And Persistence
The declared structures are embedded in longer-lived WILC state from `netdev.h` or allocated transiently for TX/RX queue entries. Register constants represent persistent device and firmware state, while packet header bit fields define transient host-to-firmware and firmware-to-host wire formats. Chip id helper behavior must remain stable because probe, init, start, wake, sleep, and interrupt code branch on it.

## Dependencies And Integration Points
Includes Linux type and bitfield helpers, and is included by bus, core, config, netdev, and cfg80211 files. It bridges Linux networking objects to firmware-facing WILC protocol details and is the common dependency that keeps SDIO/SPI backends aligned with the core.

## Risks
A wrong register constant or bit mask impacts all bus types. The duplicated `ETHERNET_HDR_LEN` definition is harmless but noisy. Several packet and VMM fields rely on exact firmware layout and little-endian handling in implementation files. `struct wilc_hif_func` is a wide callback table, so adding a callback or changing semantics requires synchronized updates to both bus backends. Buffer-size constants are hard limits for aggregation and RX storage.

## Test Signals
Header changes should be validated indirectly by building all WILC bus variants and running SDIO/SPI probe, firmware start, interrupts, TX aggregation, RX parsing, and WID config traffic. Static analysis should catch callback signature mismatches and bitfield misuse; runtime tests should focus on WILC1000 versus WILC3000 register branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan.h -->

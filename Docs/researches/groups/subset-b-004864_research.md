# Research: subset-b-004864

Grouped research for `subset-b-004864`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/sdio.c

## Purpose
This file is the SDIO bus binding for the Microchip WILC1000/WILC3000 wireless driver. It registers the `wilc1000_sdio` driver, adapts Linux SDIO CMD52/CMD53 operations to the common `struct wilc_hif_func` host-interface table, probes the chip, registers cfg80211/wiphy state, creates the first station netdev, and handles SDIO suspend/resume.

## Important APIs, Types, And Functions
The private `struct wilc_sdio` tracks SDIO-specific state: whether out-of-band IRQ GPIO mode is used, the negotiated block size, initialization state, and a small global CMD53 bounce buffer for register-sized transfers. `struct sdio_cmd52` and `struct sdio_cmd53` are compact command descriptors consumed by `wilc_sdio_cmd52()` and `wilc_sdio_cmd53()`.

Driver entry points are `wilc_sdio_probe()`, `wilc_sdio_remove()`, `wilc_sdio_suspend()`, and `wilc_sdio_resume()`. The exported host-interface table `wilc_hif_sdio` supplies `hif_init`, `hif_deinit`, register read/write, block RX/TX, interrupt read/clear/size, interrupt sync, IRQ claim/release, reset, and init-status callbacks to the WILC core in `wlan.c`.

Core bus helpers include `wilc_sdio_set_func0_csa_address()` for AHB window selection through function-0 FBR CSA registers, `wilc_sdio_set_block_size()` for CCCR block-size programming, `wilc_sdio_read_reg()` and `wilc_sdio_write_reg()` for vendor register and AHB register access, and `wilc_sdio_read()`/`wilc_sdio_write()` for aligned CMD53 block and byte transfers.

## Control Flow
Probe allocates `struct wilc_sdio` and its CMD53 bounce buffer, calls `wilc_cfg80211_init()` with `WILC_HIF_SDIO` and `wilc_hif_sdio`, discovers optional out-of-band IRQ mapping from device tree when enabled, binds driver data to the `sdio_func`, enables the optional RTC clock, temporarily initializes the SDIO function, reads the chip id, registers cfg80211, loads the MAC address from chip NVM, deinitializes the SDIO function, and creates a default station interface through `wilc_netdev_ifc_init()`.

SDIO initialization enables function-1 CSA, programs 512-byte block size for functions 0 and 1, enables function 1, waits for IOR readiness, and enables master/function interrupt bits in `SDIO_CCCR_IENx`. Deinit disables interrupts, disables functions, clears function-1 CSA, and marks the bus uninitialized. Register access routes low vendor-specific addresses 0xf0-0xff through CMD52 and all other addresses through function-0 CSA plus CMD53 data register access. Bulk transfers use function 1 when `addr == 0` and function 0 CSA windows otherwise.

Interrupt handling either claims the SDIO IRQ and calls `wilc_handle_isr()` with the SDIO host temporarily released, or configures external IRQ bits through `wilc_sdio_sync_ext()`. `wilc_sdio_read_int()` combines the firmware DMA size and IRQ flags into the common interrupt status word. `wilc_sdio_clear_int_ext()` translates common clear/VMM bits to WILC1000 or WILC3000 SDIO control registers.

Suspend disables the optional RTC clock, notifies firmware of host sleep, disables SDIO IRQs, and requests `MMC_PM_KEEP_POWER`. Resume re-enables the RTC clock, reinitializes SDIO, reclaims IRQs, and sends host wake notification.

## State And Persistence
Persistent bus state is limited to `wilc->bus_data` (`struct wilc_sdio`), `wilc->dev`, `wilc->dev_irq_num`, the optional `wilc->rtc_clk`, and `sdio_set_drvdata()`. Firmware-visible state such as function enable, block size, CSA, IRQ enable, VMM table selection, and wake/sleep status is reprogrammed by init/resume and cleared by deinit. The wiphy/netdev objects created during probe persist until remove.

## Dependencies And Integration Points
This file depends on Linux MMC/SDIO core APIs, DT IRQ lookup, optional clock handling, WILC cfg80211/netdev setup, and the common WILC core bus contract in `wlan.h`. It is paired with `wlan.c` for actual TX/RX/VMM, firmware lifecycle, and power-save handshakes, and with `wlan_cfg.c` for configuration packet responses.

## Risks
The CMD52/CMD53 paths manually set `func->num` and `func->cur_blksize`, so concurrent or unexpected SDIO core use would be risky without the surrounding host claim. AHB register access depends on correct three-byte CSA programming and little-endian conversion. IRQ flag mapping differs between WILC1000 and WILC3000 and between SDIO IRQ and external GPIO modes. Probe error paths must pair wiphy registration, IRQ mapping disposal, netdev cleanup, and private buffer free without double-free. Suspend/resume assumes firmware sleep notification succeeds before SDIO IRQs are disabled.

## Test Signals
Useful validation includes SDIO probe/remove with and without out-of-band IRQ GPIO, successful chip-id read and NVM MAC load, block and byte CMD53 transfers around 512-byte boundaries, interrupt delivery and VMM clear for WILC1000 and WILC3000, suspend/resume with `MMC_PM_KEEP_POWER`, firmware wake/sleep notification, and error-injection on CMD52/CMD53 failures. Runtime signals are absence of SDIO core warnings, successful cfg80211 registration, RX/TX progress through `wilc_handle_isr()`, and clean module unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/spi.c

## Purpose
This file is the SPI bus binding and protocol implementation for the Microchip WILC1000/WILC3000 wireless driver. It registers `wilc1000_spi`, manages optional power/reset GPIOs and RTC clocking, implements the WILC SPI command protocol including DMA transfers and command/data CRC support, and exposes the common WILC host-interface operations through `wilc_hif_spi`.

## Important APIs, Types, And Functions
Module parameters `enable_crc7` and `enable_crc16` control command and data checksum protection. `struct wilc_spi` stores bus initialization state, CRC probing state, active CRC mode, and optional enable/reset GPIO descriptors. Packed protocol structures `struct wilc_spi_cmd`, `struct wilc_spi_rsp_data`, `struct wilc_spi_read_rsp_data`, and `struct wilc_spi_special_cmd_rsp` describe the command/response wire layout.

Probe/remove are handled by `wilc_bus_probe()` and `wilc_bus_remove()`. Low-level transfer helpers are `wilc_spi_tx()`, `wilc_spi_rx()`, and `wilc_spi_tx_rx()`. Protocol helpers include `wilc_spi_single_read()`, `wilc_spi_write_cmd()`, `wilc_spi_dma_rw()`, `spi_data_write()`, `spi_data_rsp()`, `wilc_spi_special_cmd()`, `spi_internal_read()`, and `spi_internal_write()`. Host-interface callbacks are implemented by `wilc_spi_init()`, `wilc_spi_deinit()`, `wilc_spi_read_reg()`, `wilc_spi_write_reg()`, `wilc_spi_read()`, `wilc_spi_write()`, `wilc_spi_read_int()`, `wilc_spi_clear_int_ext()`, `wilc_spi_sync_ext()`, and `wilc_spi_reset()`.

## Control Flow
Probe allocates SPI private state, initializes common WILC cfg80211 state with `WILC_HIF_SPI`, records the SPI IRQ as `wilc->dev_irq_num`, parses optional `enable` and `reset` GPIOs, enables the optional RTC clock, powers the chip, configures the SPI protocol, reads the chip id, registers cfg80211, loads the MAC address from NVM, powers the chip back down, and creates the default station netdev.

The protocol starts by inferring the chip's current CRC7 setting in `wilc_spi_configure_bus_protocol()`: it tries internal reads with the requested CRC7 mode and then the opposite mode, disables CRC16 checks during probing, writes the desired CRC7/CRC16 and 8 KiB data packet size into the protocol register, and updates `struct wilc_spi` to match. Register reads/writes choose internal commands for clockless addresses and single read/write commands for normal registers. On non-clockless failures, the code retries up to `SPI_RETRY_MAX_LIMIT`, issuing a WILC reset command and short delay between attempts.

DMA block writes first send a DMA EXT WRITE command, stream one or more data packets tagged first/inner/last, optionally append CRC16 per data packet, then read and validate the final data response. DMA reads send a DMA EXT READ command, poll for each data-start header, read packet chunks, and optionally validate CRC16. Interrupt sync programs pin mux and interrupt-enable registers. Clear uses an internal write/read retry to ensure `EN_VMM` took effect.

## State And Persistence
The active bus state is `struct wilc_spi`: `isinit`, CRC mode booleans, and GPIOs. `wilc_wlan_power()` persists physical chip power state through enable/reset GPIO levels. Firmware-visible SPI protocol state persists in the WILC SPI protocol register and may survive module unload, which is why CRC probing is needed. The common WILC object owns cfg80211, netdev, chip id, and power-save state.

## Dependencies And Integration Points
This file integrates with Linux SPI, GPIO descriptor APIs, optional clock APIs, CRC7 and CRC-ITU-T helpers, WILC cfg80211/netdev setup, and the common WILC `wlan.c` core through `struct wilc_hif_func`. It relies on register constants and chip id helpers from `wlan.h`, and on board descriptions providing usable IRQ, reset, and optional enable pins.

## Risks
SPI command parsing is sensitive to undocumented response padding before the data start tag; the code searches a bounded extra header area. CRC probing can misdiagnose bus faults as CRC mismatch. TX/RX helper allocations per transfer are simple but can be expensive on high-rate paths. Retry/reset recovery is disabled for clockless registers and can still leave the chip in a partially configured protocol state. `wilc_spi_read()` and `wilc_spi_write()` reject transfers of four bytes or less, so callers must use register helpers for small accesses. Error unwind in probe must power down before freeing common objects.

## Test Signals
Test SPI probe with reset-only and enable+reset GPIO wiring, requested CRC7/CRC16 modes, module unload/reload without hardware reset, high SPI clock reads that trigger padded response handling, DMA transfers larger than 8 KiB, register access to clockless and normal addresses, interrupt clear/sync, and induced SPI transaction failures to exercise reset retry. Successful signals include stable chip id validation, NVM MAC load, cfg80211 registration, TX/RX traffic, and no CRC mismatch logs under clean wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan.c

## Purpose
This is the common WILC data-path, firmware-lifecycle, power-management, and configuration transport core shared by SDIO and SPI bus backends. It owns TX/RX queues, TCP ACK filtering, access-category flow control, bus wake/sleep locking, VMM table aggregation, interrupt dispatch, firmware download/start/stop, WID configuration packet commit/wait logic, chip-id detection, NVM MAC loading, and per-netdev runtime allocation.

## Important APIs, Types, And Functions
Public entry points include `wilc_wlan_init()`, `wilc_wlan_cleanup()`, `wilc_wlan_firmware_download()`, `wilc_wlan_start()`, `wilc_wlan_stop()`, `wilc_handle_isr()`, `wilc_wlan_handle_txq()`, `wilc_wlan_txq_add_net_pkt()`, `wilc_wlan_txq_add_mgmt_pkt()`, `wilc_wlan_cfg_set()`, `wilc_wlan_cfg_get()`, `wilc_send_config_pkt()`, `host_wakeup_notify()`, `host_sleep_notify()`, `wilc_get_chipid()`, `wilc_load_mac_from_nv()`, and `wilc_enable_tcp_ack_filter()`.

Key internal helpers manage queue lists (`wilc_wlan_txq_add_to_tail()`, `wilc_wlan_txq_add_to_head()`, `wilc_wlan_txq_remove_from_head()`, `wilc_wlan_rxq_add()`, `wilc_wlan_rxq_remove()`), classify traffic (`ac_classify()`, `ac_change()`, `ac_balance()`, `ac_update_fw_ac_pkt_info()`), suppress duplicate TCP ACKs (`tcp_process()` and `wilc_wlan_txq_filter_dup_tcp_ack()`), wake/sleep chips (`chip_wakeup_wilc1000()`, `chip_wakeup_wilc3000()`, `chip_allow_sleep_wilc1000()`, `chip_allow_sleep_wilc3000()`), and parse RX buffers (`wilc_wlan_handle_rx_buff()` and `wilc_wlan_handle_rxq()`).

## Control Flow
Initialization clears `quit`, initializes the selected HIF if needed, validates the chip id, allocates VMM, TX, and RX buffers, then calls `init_chip()` to configure boot-from-IRAM reset muxes and WILC3000 boot registers. Firmware download resets Cortus, iterates firmware address/size records, and writes chunks through the HIF block TX path. Start configures the VMM core for SDIO or SPI, passes IRQ/sleep-clock flags in `WILC_GP_REG_1`, syncs external interrupts, toggles reset bits, and starts firmware execution. Stop disables WiFi mode and sleep power sequencing, then sets the abort bit in `WILC_GP_REG_0`.

Network and management TX enqueue functions allocate `txq_entry_t`, reject when quitting or uninitialized, classify network packets into WMM access categories, apply firmware ACM remapping and host queue limiting, optionally record pure TCP ACKs for duplicate suppression, and signal `txq_event`. Config packets are pushed to the voice queue head to reduce control latency. `wilc_wlan_handle_txq()` wakes/acquires the bus, optionally filters duplicate ACKs, reads firmware AC queue state, builds a VMM table for queued packets, waits for firmware entries, copies selected frames into the aggregated TX buffer with WILC host headers and BSSID/priority metadata, completes per-packet callbacks, clears/enables TX VMM, and block-transfers the aggregate buffer.

Interrupt dispatch acquires and wakes the bus, reads the HIF interrupt status, handles `DATA_INT_EXT` by computing the RX byte size, enabling RX VMM, reading the RX data into a ring-like host buffer, enqueueing an RX entry, and parsing it immediately. RX parsing demultiplexes management frames to `wilc_wfi_mgmt_rx()`, data frames to `wilc_frmw_to_host()`, and config frames to `wilc_wlan_cfg_indicate_rx()`, completing `cfg_event` for matching config replies or calling `wilc_mac_indicate()` for status updates.

Configuration setters/getters serialize through `cfg_cmd_lock`, append WID fields into `wilc->cfg_frame`, commit on the final WID with command type `W` or `Q`, enqueue the config packet, wait up to `WILC_CFG_PKTS_TIMEOUT` for `cfg_event`, then advance the sequence number. `wilc_send_config_pkt()` is the higher-level loop over multiple WIDs.

## State And Persistence
Persistent runtime state is in `struct wilc`: HIF function table, initialized/quit flags, power-save mode, chip id, VMM/TX/RX buffers, TX queues per AC, RX queue, locks/completions, `cfg_frame`, config sequence number, cached firmware AC queue stats, and NVM MAC address. Per-vif state includes BSSID and TCP ACK filter arrays. Hardware state includes wake/sleep bits, VMM tables, interrupt registers, global mode/reset registers, and firmware configuration WIDs. Most firmware state is not persistent across reset and must be replayed by higher cfg80211/netdev flows.

## Dependencies And Integration Points
This file is bus-neutral but depends on `struct wilc_hif_func` supplied by SDIO or SPI. It integrates with cfg80211/netdev helpers for RX delivery, management frame handling, scan/network notifications, MAC status indication, and VIF indexing. It also depends on `wlan_cfg.c` for WID serialization/parsing and on `wlan.h` register/bit definitions.

## Risks
Queue and completion ordering is safety-critical: config packets rely on matching sequence numbers and prompt RX parsing, while TX callbacks are invoked before the aggregate transfer is submitted to the device. VMM entry accounting and AC balancing must stay synchronized with firmware queue stats or packets can be starved or retried indefinitely. RX uses offsets into a reusable host buffer; consumers must finish before that region is overwritten. Power-save bus acquisition sleeps/wakes chips while holding `hif_cs`, so HIF callbacks must not reenter this lock. Firmware download has a leak-style early return if `acquire_bus()` fails after allocating `dma_buffer`. WILC1000/WILC3000 and SDIO/SPI register differences increase regression risk.

## Test Signals
Exercise firmware download/start/stop, netdev open/close, sustained data TX across all ACs, TCP ACK filtering on/off, management TX completion, config WID get/set timeout and success paths, RX data/config/status/scan/mgmt frames, interrupt storms with unknown status, VMM full retry behavior, chip wake/sleep in power-save mode, NVM MAC extraction across banks, and WILC1000/WILC3000 chip-id variants. Lockdep, KASAN, packet loss counters, firmware logs, and netdev queue progress are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.c

## Purpose
This file serializes WILC WID configuration requests and parses firmware configuration, status, network-info, and scan-complete responses. It maintains a small cache of queried WID values for byte, halfword, word, and string responses and dispatches asynchronous firmware notifications into the higher host-interface/cfg80211 layer.

## Important APIs, Types, And Functions
Static WID cache templates are `g_cfg_byte`, `g_cfg_hword`, `g_cfg_word`, and `g_cfg_str`. Encoding helpers are `wilc_wlan_cfg_set_byte()`, `wilc_wlan_cfg_set_hword()`, `wilc_wlan_cfg_set_word()`, `wilc_wlan_cfg_set_str()`, and `wilc_wlan_cfg_set_bin()`. Parsing helpers are `wilc_wlan_parse_response_frame()` and `wilc_wlan_parse_info_frame()`.

Public functions are `wilc_wlan_cfg_set_wid()`, `wilc_wlan_cfg_get_wid()`, `wilc_wlan_cfg_get_val()`, `wilc_wlan_cfg_indicate_rx()`, `wilc_wlan_cfg_init()`, and `wilc_wlan_cfg_deinit()`.

## Control Flow
Set WID serialization chooses an encoder from the WID type nibble, writes id and little-endian length, copies payload, and for binary WIDs appends an additive checksum. Get serialization writes only the WID id. Firmware config replies arrive through `wilc_wlan_cfg_indicate_rx()`, which strips the four-byte response header and switches on message type. Config replies update cached values by walking the matching cache table. Status info updates `WID_STATUS`, marks the response as a status packet, and also calls `wilc_gnrl_async_info_received()`. Network and scan messages are forwarded to `wilc_network_info_received()` and `wilc_scan_complete_received()`.

Initialization duplicates the static cache templates, allocates one `struct wilc_cfg_str_vals`, and wires string cache entries for firmware version, MAC address, and association response. Deinit frees all duplicated arrays and string storage.

## State And Persistence
The persistent state is `wl->cfg`, which owns dynamically duplicated cache arrays and backing buffers for string WIDs. Cached byte/word/string values persist until overwritten by a later response or freed. The actual firmware configuration is stored in firmware; this layer only constructs requests and caches selected replies.

## Dependencies And Integration Points
This file depends on WID ids and type encoding from `wlan_if.h`, packet/frame constants from `wlan.h`, and WILC async notification functions from the netdev/cfg80211 side. It is called by `wlan.c` when constructing config packets and when RX demux finds a config packet.

## Risks
Bounds checks are simple and return zero on oversized output; callers interpret zero as timeout/failure, so malformed WID sizes can look like transport failure. Halfword and word set functions cast `u8 *` to integer pointers, which assumes sufficient alignment from callers. String response parsing copies the length prefix plus payload into the cached string buffer and rejects oversize responses. The binary checksum is additive and not strong. Unknown WIDs are silently ignored unless callers expect a cached value.

## Test Signals
Exercise byte, word, string, and binary WID set/get operations; firmware-version, MAC-address, RSSI, status, link-speed, and association-response queries; scan complete and network info notifications; malformed response lengths; and config packet timeout behavior. Memory-leak checks should cover init/deinit failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.h

## Purpose
This header declares the WILC configuration cache data structures and the public WID serialization/parsing functions implemented by `wlan_cfg.c`.

## Important APIs, Types, And Functions
It defines `struct wilc_cfg_byte`, `struct wilc_cfg_hword`, `struct wilc_cfg_word`, `struct wilc_cfg_str`, `struct wilc_cfg_str_vals`, and `struct wilc_cfg`. The public API consists of `wilc_wlan_cfg_set_wid()`, `wilc_wlan_cfg_get_wid()`, `wilc_wlan_cfg_get_val()`, `wilc_wlan_cfg_indicate_rx()`, `wilc_wlan_cfg_init()`, and `wilc_wlan_cfg_deinit()`.

## Control Flow
The header has no execution path. It specifies the shape used by initialization to allocate caches, by config packet construction to serialize WIDs, and by RX config demux to update cached values and notify waiters.

## State And Persistence
`struct wilc_cfg` is embedded in `struct wilc` and holds dynamically allocated arrays plus `struct wilc_cfg_str_vals`, which persists firmware version, MAC address, and association response buffers while the WILC object is alive.

## Dependencies And Integration Points
This header depends on `WILC_MAX_ASSOC_RESP_FRAME_SIZE` from `wlan_if.h` via including contexts and forward-declares `struct wilc`. It is included by `wlan.c` and `wlan_cfg.c`.

## Risks
The declarations encode buffer sizes and cache ownership expectations; changing them requires matching allocation/free and parser updates. Consumers must call init before config traffic and deinit during common cleanup to avoid NULL dereferences or leaks.

## Test Signals
Build coverage catches API drift. Runtime validation comes from WID get/set success, association response retrieval, firmware version retrieval, and clean WILC teardown under leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_if.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_if.h

## Purpose
This header defines the WILC firmware configuration interface: enums for firmware operating/security/power/scan/HT modes, bus wake/sleep acquisition policy, the generic `struct wid` request descriptor, and the large WID id namespace used for host-to-firmware configuration and firmware-to-host status.

## Important APIs, Types, And Functions
Important enums cover BSS type, 11g mode, preamble, active/passive scan, power-save mode, bus acquire/release behavior, security bit composition, authentication type, MFP policy, site survey mode, ACK policy, rekey policy, scan filters, 11n protection/operation/SMPS, TX rates, scan request type, management frame registration indexes, and WID wire types. `struct wid` is the common descriptor used by `wilc_send_config_pkt()` callers.

The WID list maps typed ids for basic MAC settings, counters, strings, keys, association data, PMKID, remain-on-channel, external authentication, station/AP management, multicast filter, and firmware/hardware metadata.

## Control Flow
This header does not execute code. Its values drive config packet assembly in `wlan.c`/`wlan_cfg.c` and higher cfg80211 operations that translate Linux wireless requests into firmware WID set/get sequences.

## State And Persistence
The enums and WID ids describe firmware-persistent settings such as BSS type, channel, security mode, keys, beacon interval, retry limits, power-save mode, multicast filters, and station entries. On the host side, `struct wid` values are transient request descriptors and selected responses are cached by `struct wilc_cfg`.

## Dependencies And Integration Points
Includes Linux netdevice definitions and WILC firmware helpers from `fw.h`. It is consumed by WILC cfg80211, host-interface, core config, and data-path files. It is the main symbolic bridge between Linux cfg80211 concepts and Microchip firmware WID commands.

## Risks
WID ids are firmware ABI; changing values or types breaks device configuration. Security enums combine bit flags in firmware-specific ways and must match key/install code. The type nibble is used by generic serialization, so an incorrectly typed WID will produce malformed packets. Several ids are custom or sparsely documented, increasing compatibility risk across firmware versions.

## Test Signals
Validation should cover connect/AP/key/scan/ROC/external-auth/multicast workflows that exercise diverse WIDs, plus explicit get/set tests for each WID type. Firmware logs and config reply parsing should be watched for unsupported or malformed WID errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Kconfig

## Purpose
This Kconfig file adds the pureLiFi vendor menu under Linux wireless drivers and conditionally includes the plfxlc driver Kconfig when `WLAN_VENDOR_PURELIFI` is enabled.

## Important APIs, Types, And Functions
It defines `config WLAN_VENDOR_PURELIFI` as a boolean vendor selector defaulting to yes, with help text explaining that disabling it skips pureLiFi-specific questions. The `if WLAN_VENDOR_PURELIFI` block sources `drivers/net/wireless/purelifi/plfxlc/Kconfig`.

## Control Flow
During kernel configuration, selecting the vendor gate exposes the plfxlc device-support option. It does not by itself build code; it controls visibility of subordinate symbols.

## State And Persistence
The persistent output is the generated kernel `.config` choice for `WLAN_VENDOR_PURELIFI` and subordinate plfxlc symbols.

## Dependencies And Integration Points
Integrated by the parent wireless Kconfig tree. It delegates actual module selection and dependencies to `plfxlc/Kconfig`.

## Risks
If the source path changes or the vendor gate is disabled, the plfxlc option disappears from configuration menus. Default-y vendor gates increase menu visibility but do not force a module build.

## Test Signals
Run menuconfig/olddefconfig with the vendor symbol enabled and disabled and verify `CONFIG_PLFXLC` visibility and generated Makefile traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Makefile

## Purpose
This Makefile descends into the pureLiFi plfxlc driver directory when `CONFIG_PLFXLC` is enabled.

## Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_PLFXLC) := plfxlc/`.

## Control Flow
Kbuild evaluates the config symbol and includes the `plfxlc/` subdirectory in the wireless driver build only when the driver is selected.

## State And Persistence
No runtime state exists. The persistent effect is build graph membership for the plfxlc module or built-in object tree.

## Dependencies And Integration Points
Depends on `CONFIG_PLFXLC` from `purelifi/plfxlc/Kconfig` and on Kbuild's directory traversal semantics.

## Risks
The rule is intentionally narrow; adding more pureLiFi drivers would require additional object entries. Misnaming `CONFIG_PLFXLC` or the directory would silently omit the driver.

## Test Signals
Build with `CONFIG_PLFXLC=m` and confirm `drivers/net/wireless/purelifi/plfxlc/plfxlc.ko` is produced; build with it disabled and confirm no descent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Kconfig

## Purpose
This Kconfig file defines the pureLiFi X/XL/XC USB LiFi driver option.

## Important APIs, Types, And Functions
`config PLFXLC` is a tristate option named "pureLiFi X, XL, XC device support". It depends on `CFG80211`, `MAC80211`, and `USB`. Help text states that the driver supports pureLiFi USB adapters based on an 802.11 OFDM PHY using light as the medium and common 802.11 authentication/encryption modes.

## Control Flow
When selected as built-in or module, Kbuild compiles the plfxlc object list. As a module, the resulting module name is `plfxlc`.

## State And Persistence
The selected value persists in the kernel `.config` as `CONFIG_PLFXLC`.

## Dependencies And Integration Points
The option is sourced by the parent pureLiFi vendor Kconfig and consumed by the plfxlc Makefile. The dependencies match the code's use of USB device IDs, mac80211 hardware registration, and cfg80211/wiphy integration.

## Risks
Missing dependency updates could allow build failures if code gains new subsystem calls. Because the option is a driver leaf under a default-y vendor menu, users still need to explicitly select the device support.

## Test Signals
Kconfig validation should show `PLFXLC` unavailable without USB/mac80211/cfg80211 and buildable as module or built-in when dependencies are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Makefile

## Purpose
This Makefile builds the pureLiFi plfxlc driver object from its implementation files.

## Important APIs, Types, And Functions
It declares `obj-$(CONFIG_PLFXLC) := plfxlc.o` and composes `plfxlc-objs` from `chip.o`, `firmware.o`, `usb.o`, and `mac.o`.

## Control Flow
Kbuild links the four implementation objects into one built-in or module object according to `CONFIG_PLFXLC`.

## State And Persistence
No runtime state exists; the file defines build-time object composition.

## Dependencies And Integration Points
This integrates with the parent pureLiFi Makefile and the Kconfig symbol. It reflects the driver layering: chip control, firmware staging, USB transport, and mac80211 integration.

## Risks
Adding a new source file without updating `plfxlc-objs` will omit code. Object order is simple and should not matter except for module init/exit symbols in `usb.o`.

## Test Signals
Build with `CONFIG_PLFXLC=m` and verify all four object files are compiled and linked into `plfxlc.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.c

## Purpose
This file implements pureLiFi chip-level control on top of the USB transport. It initializes/releases the chip wrapper, logs hardware identity, sets beacon interval, toggles radio power, enables/disables RX/TX, and writes the selected PHY rate.

## Important APIs, Types, And Functions
Public functions are `plfxlc_chip_init()`, `plfxlc_chip_release()`, `plfxlc_set_beacon_interval()`, `plfxlc_chip_init_hw()`, `plfxlc_chip_switch_radio()`, `plfxlc_chip_enable_rxtx()`, `plfxlc_chip_disable_rxtx()`, and `plfxlc_chip_set_rate()`.

## Control Flow
`plfxlc_chip_init()` zeroes `struct plfxlc_chip`, initializes its mutex, and initializes embedded USB state. `plfxlc_chip_init_hw()` logs USB vendor/product/device version, permanent MAC address, and speed, then programs a default 100 TU beacon interval. Radio and rate changes are sent as USB vendor/write requests. RX/TX enable starts TX first and then RX; disable writes `USB_REQ_RXTX_WR` value zero before shutting down RX and TX queues/URBs.

## State And Persistence
`struct plfxlc_chip` stores the embedded USB transport, mutex, unit type, link LED value, beacon interval, and beacon-set flag. Device-side radio/rate/beacon state persists in firmware until changed, reset, or unplugged.

## Dependencies And Integration Points
Depends on `plfxlc_usb_wreq()`, `plfxlc_usb_enable_tx()`, `plfxlc_usb_enable_rx()`, `plfxlc_usb_disable_rx()`, `plfxlc_usb_disable_tx()`, and `plfxlc_mac_get_perm_addr()`. It is called by `mac.c` during hardware initialization and by `usb.c` during probe and disconnect.

## Risks
Beacon interval caching suppresses duplicate interval writes but ignores `dtim_period` and `type`. Radio/rate writes are synchronous USB bulk requests and can fail during disconnect/reset. RX/TX enable has partial failure risk if TX is enabled and RX enable fails. The chip mutex is initialized but not used in these operations, so callers must provide any needed serialization.

## Test Signals
Probe should log identity and set the default beacon interval. Validate radio on/off, rate setting, RX/TX enable/disable during probe/disconnect, and beacon interval updates from adhoc BSS changes. USB request failures should produce error logs and clean unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.h

## Purpose
This header declares the pureLiFi chip wrapper, radio/unit enums, multicast hash helper, and chip-level control APIs used by the mac80211 and USB layers.

## Important APIs, Types, And Functions
It defines `enum unit_type`, radio constants `PLFXLC_RADIO_OFF` and `PLFXLC_RADIO_ON`, `struct plfxlc_chip`, `struct plfxlc_mc_hash`, `plfxlc_chip_dev()`, API prototypes for chip init/release/RXTX/rate/beacon/radio control, `plfxlc_usb_to_chip()`, and `plfxlc_mc_add_all()`.

## Control Flow
The inline helpers convert from embedded USB object to chip object and set multicast hash fields to all ones. All other execution is in `chip.c`.

## State And Persistence
`struct plfxlc_chip` embeds `struct plfxlc_usb`, a mutex, unit type, link LED, and beacon interval cache. It is embedded in `struct plfxlc_mac`, so its lifetime follows the mac80211 hardware object.

## Dependencies And Integration Points
Includes mac80211 and `usb.h`. It is included by `chip.c`, `mac.c`, and `usb.c`, making it the local bridge between MAC and USB transport state.

## Risks
Because `chip.h` includes `usb.h` and `usb.h` references chip/mac conversion helpers elsewhere, include ordering must avoid circular compile issues. The multicast helper blindly enables all hash bits and depends on firmware interpretation.

## Test Signals
Compile coverage and runtime probe/release validate structure layout and conversion helpers. Multicast filter tests validate `plfxlc_mc_add_all()` through `configure_filter()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/firmware.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/firmware.c

## Purpose
This file handles pureLiFi firmware and device metadata transfers over USB vendor control and bulk endpoints. It downloads FPGA images for LiFi X/XC devices, downloads packed XL firmware for LiFi XL devices, and reads MAC address, serial number, and firmware version from the device.

## Important APIs, Types, And Functions
Internal helpers are `send_vendor_request()` for USB control IN and `send_vendor_command()` for USB control OUT. Public functions are `plfxlc_download_fpga()`, `plfxlc_download_xl_firmware()`, and `plfxlc_upload_mac_and_serial()`.

## Control Flow
`plfxlc_download_fpga()` selects `plfxlc/lifi-x.bin` or `plfxlc/lifi-xc.bin` from USB IDs, requests firmware, asks the device for FPGA setup status, sends a setup command, validates the magic endpoint byte, streams bit-reversed firmware blocks over bulk OUT to the indicated endpoint, reads FPGA state, validates success, sends the state command, and delays for device settle time.

`plfxlc_download_xl_firmware()` sends the XL firmware-start command, loads `plfxlc/lifi-xl.bin`, reads the packed file count and total size, rejects more than ten embedded files or oversized pieces, iterates embedded file offsets, sends file-select commands, sends 64-byte data chunks for each file, then sends the execute command. `plfxlc_upload_mac_and_serial()` reads MAC, serial, and firmware version through vendor requests and copies them into caller-provided buffers.

## State And Persistence
The function-local firmware metadata and DMA buffers are transient. Device firmware/FPGA state persists on the USB device after successful download until reset/disconnect. MAC and serial are copied into the `plfxlc_mac`/probe-local state managed by `usb.c`.

## Dependencies And Integration Points
Uses Linux firmware loader, USB control/bulk APIs, `bitrev8()`, and constants from `usb.h`/`intf.h`. Called from `usb.c` probe before USB reset/configuration and mac80211 hardware initialization.

## Risks
Firmware file parsing trusts embedded offsets enough that malformed files can produce out-of-range reads if not covered by size checks; XL size checks reject individual sizes over 60000 but do not comprehensively validate every offset before memcpy. FPGA transfer allocates and frees one block copy per chunk. Several vendor requests ignore return codes, so failed setup/status reads can become later validation errors. `plfxlc_download_xl_firmware()` logs intermediate failures but returns zero after the execute command path unless earlier fatal errors return, which can mask transfer issues.

## Test Signals
Test all supported USB IDs, missing firmware files, malformed XL pack headers, FPGA magic/state failures, bulk transfer errors, and metadata reads. Probe logs should show firmware version and selected image; successful probe should continue through radio enable and mac80211 registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/intf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/intf.h

## Purpose
This header defines pureLiFi USB vendor request IDs, data alignment constants, firmware metadata lengths, AP station limits, RX status wire format, and the generic USB request wrapper used by control/bulk write helpers.

## Important APIs, Types, And Functions
Definitions include `PURELIFI_BYTE_NUM_ALIGNMENT`, `AP_USER_LIMIT`, FPGA and XL vendor command/request IDs, metadata request IDs, `PLF_SERIAL_LEN`, `PLF_FW_VER_LEN`, `struct rx_status`, `enum plf_usb_req_enum`, and `struct plf_usb_req`.

## Control Flow
No direct runtime flow exists. The values drive firmware download, metadata upload, USB request packet construction, RX status parsing, beacon/rate/power writes, and data TX commands.

## State And Persistence
`struct rx_status` is transient device-to-host metadata prepended to RX frames. `struct plf_usb_req` is a host-to-device request envelope. Constants describe persistent firmware request ABI.

## Dependencies And Integration Points
Included by `usb.h`, which propagates these constants to firmware, USB, chip, and MAC code. The definitions must match the pureLiFi firmware protocol.

## Risks
This header locally defines `ETH_ALEN` instead of relying on the canonical Linux definition, which can conflict if include order changes. Request ids and packed structure layout are firmware ABI and fragile. `PLF_SERIAL_LEN` here is 14, while `usb.h` later defines `PURELIFI_SERIAL_LEN` as 256 for host storage; callers must use the correct length constant.

## Test Signals
Build and sparse checks should catch type/packing drift. Runtime validation comes from successful vendor requests, RX status parsing with sane RSSI/rate/CRC counters, and data/beacon/rate/power writes accepted by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/intf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.c

## Purpose
This file implements the mac80211 integration for the pureLiFi plfxlc USB device. It advertises channels/rates, allocates and registers `ieee80211_hw`, handles TX/RX frame adaptation, filters ACKs, tracks station MACs for USB FIFO scheduling, manages minimal station/adhoc interface state, configures receive filters, handles beacon interval changes, and exposes ethtool statistics.

## Important APIs, Types, And Functions
Public helpers include `plfxlc_mac_alloc_hw()`, `plfxlc_mac_release_hw()`, `plfxlc_mac_preinit_hw()`, `plfxlc_mac_init_hw()`, `plfxlc_mac_rx()`, `plfxlc_mac_tx_to_dev()`, `plfxlc_op_start()`, `plfxlc_op_stop()`, and `plfxlc_restore_settings()`. The `ieee80211_ops` table `plfxlc_ops` supplies TX, start/stop, interface add/remove, config, filter, BSS change, stats, and ethtool callbacks while using mac80211 emulation for channel-context operations.

Key internal functions are `plfxlc_fill_ctrlset()` for USB TX headers and alignment, `plfxlc_op_tx()` for data versus management TX dispatch, `plfxlc_mac_tx_status()` for mac80211 completion, `plfxlc_filter_ack()` for ACK matching, `plfxlc_op_configure_filter()`, and `plfxlc_op_bss_info_changed()`.

## Control Flow
Allocation creates an `ieee80211_hw`, initializes private `struct plfxlc_mac`, copies static 2.4 GHz/LC channels and 802.11b/g-like rates, sets `NL80211_BAND_LC`, enables RX-includes-FCS, dBm signal reporting, host broadcast buffering, and MFP capability, restricts interface modes to station and adhoc, reserves extra TX headroom, initializes ACK queues, and initializes the embedded chip/USB state.

TX prepends `struct plfxlc_ctrlset`, pads packets to 4-byte alignment and away from exact 512-byte multiples, stores `hw` in `rate_driver_data[0]`, and for data frames maps the destination MAC to a tracked station queue or broadcast queue. It stops mac80211 queues when a station queue exceeds 60 SKBs, drops above 256, enqueues the SKB, and asks USB to send the next queued packet round-robin. Non-data frames are sent immediately with `plfxlc_usb_wreq_async()`.

RX parses the device `rx_status`, synthesizes `ieee80211_rx_status` with fixed 2412 MHz LC band and RSSI conversion, updates CRC/rssi counters, optionally consumes ACK frames, reads a big-endian payload length, validates MTU, applies padding for QoS/A4 alignment, updates the station table and heartbeat flags from source address, allocates an SKB, copies the 802.11 payload, and delivers it with `ieee80211_rx_irqsafe()`.

Interface add accepts only one station or adhoc VIF. BSS info changes update association state and, for adhoc beacon changes, fetch/free the beacon and program beacon interval. Filter configuration records FCS/control pass-through and multicast hash state.

## State And Persistence
`struct plfxlc_mac` persists the active `ieee80211_vif`, interface type, beacon cache, multicast hash, ACK wait queue, channels/rates/band, embedded chip, serial/MAC buffers, pass flags, ACK state, association flag, channel/regdomain fields, CRC error counter, and RSSI. USB TX station queues and flags are embedded under the chip's USB object. Firmware owns actual radio, rate, beacon, and data FIFO state.

## Dependencies And Integration Points
Depends on mac80211/cfg80211 APIs, USB transport helpers from `usb.c`, chip control from `chip.c`, request/status structures from `mac.h`/`intf.h`, and firmware behavior around ACKs/FIFO messages. Probe in `usb.c` calls allocation/preinit/register/init paths and RX URBs call `plfxlc_mac_rx()`.

## Risks
`struct plfxlc_header` overlays frame data with a pointer field for destination MAC, which is unusual for a wire header and depends on local layout assumptions. ACK handling comments admit it may need fixing; queued SKBs can be completed optimistically. TX queue thresholds and per-station mapping are driver-local and can stop/wake all mac80211 queues based on one station's backlog. RX assumes fixed frequency and LC band and has limited CRC/error filtering. Interface support is deliberately minimal and rejects AP mode despite station table naming. Some flags such as `PURELIFI_DEVICE_RUNNING` are cleared but not set in this file.

## Test Signals
Validate station and adhoc interface creation, TX data and management frames, queue stop/wake thresholds, ACK/no-ACK completion, RX data/control/filter behavior, station heartbeat table cleanup through USB timers, beacon interval programming in adhoc mode, ethtool RSSI/CRC stats, and probe/disconnect/reset races. mac80211 debug, skb leak checks, and USB error injection are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.h

## Purpose
This header declares pureLiFi mac80211-private structures, rate constants, USB TX control header layout, RX/TX status overlays, beacon state, device flags, conversion helpers, and public MAC-layer APIs.

## Important APIs, Types, And Functions
It defines pureLiFi CCK/OFDM rate encodings, modulation-rate enum values, regulatory constants, `struct plfxlc_ctrlset`, `struct plfxlc_header`, `struct tx_status`, `struct beacon`, `enum plfxlc_device_flags`, and `struct plfxlc_mac`. Inline helpers convert between `ieee80211_hw`, chip, USB, and MAC containers and retrieve the permanent MAC address. API prototypes cover hardware allocation/release, preinit/init, RX, TX completion, start/stop, and restore.

## Control Flow
The inline helpers are used throughout USB and chip callbacks to recover enclosing objects. `struct plfxlc_ctrlset` is prepended to every outgoing frame by `mac.c`, and `struct tx_status` is available for completion status interpretation.

## State And Persistence
`struct plfxlc_mac` is the private state allocated with `ieee80211_alloc_hw()`. It persists active VIF, beacon work/cache fields, multicast hash, ACK queue, channels/rates/band, embedded chip/USB state, hardware/serial addresses, pass flags, association state, type, RSSI, and CRC counters.

## Dependencies And Integration Points
Includes Linux mac80211 and `chip.h`. Used by `mac.c`, `usb.c`, `chip.c`, and firmware helpers. The declared control header and status structures must match device firmware expectations.

## Risks
Packed overlay structures mix protocol fields and host pointers; misuse could treat packet bytes as pointers. Some declared work fields are not actively used in the current implementation. Rate constants and LC band setup must align with mac80211 expectations and firmware rate IDs.

## Test Signals
Build coverage catches API drift. Runtime validation includes TX header acceptance by firmware, RX/TX completion behavior, ethtool stats, object container conversions during USB callbacks, and clean hardware release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.c

## Purpose
This file is the USB transport, probe, runtime, and power/reset layer for the pureLiFi plfxlc driver. It matches supported USB IDs, allocates mac80211 hardware, uploads metadata, downloads firmware, configures radio and MAC address, manages RX URBs, schedules per-station TX queues, handles device FIFO/status messages, and implements disconnect, reset, suspend, and resume.

## Important APIs, Types, And Functions
The USB ID table matches pureLiFi X, XC, and XL devices. Public transport functions are `plfxlc_usb_init()`, `plfxlc_usb_release()`, `plfxlc_usb_init_hw()`, `plfxlc_usb_enable_rx()`, `plfxlc_usb_disable_rx()`, `plfxlc_usb_enable_tx()`, `plfxlc_usb_disable_tx()`, `plfxlc_usb_wreq()`, `plfxlc_usb_wreq_async()`, `plfxlc_send_packet_from_data_queue()`, `plfxlc_tx_urb_complete()`, and `plfxlc_speed()`.

Important internal functions include `rx_urb_complete()`, `alloc_rx_urb()`, `free_rx_urb()`, `__lf_x_usb_enable_rx()`, `__lf_x_usb_disable_rx()`, `get_usb_req()`, `slif_data_plane_sap_timer_callb()`, `sta_queue_cleanup_timer_callb()`, `probe()`, `disconnect()`, `pre_reset()`, `post_reset()`, `suspend()`, and `resume()`.

## Control Flow
Probe allocates `ieee80211_hw`, records `ez_usb`, reads MAC and serial, sets unit type to station, preinitializes permanent MAC, registers mac80211 hardware, downloads XL firmware or FPGA image based on USB ID, resets USB configuration, turns the radio on, sets rate 8, writes the MAC to firmware, enables RX/TX, initializes per-station queues and broadcast station, starts the retry and station-cleanup timers, initializes chip/mac hardware, and marks USB initialized.

RX enable allocates five coherent bulk-IN URBs and submits them. Completion validates device/initialization state, handles terminal URB errors, retries transient errors up to a counter, passes normal RX frames to `plfxlc_mac_rx()` when link is up, and interprets short status messages as FIFO-full, FIFO-not-full, connect, or disconnect events. RX URBs are resubmitted from the completion path.

TX scheduling is per station. `plfxlc_send_packet_from_data_queue()` scans station queues round-robin, skips disconnected or FIFO-full stations, dequeues one SKB, submits an async bulk OUT URB, and wakes mac80211 queues when backlog falls below the low threshold. TX completion hands status to `plfxlc_mac_tx_to_dev()`, sends another queued packet, and frees the URB.

Synchronous write requests build a `struct plf_usb_req` envelope, append FCS zeros and alignment padding, and send it over bulk OUT. Async writes send the caller's buffer directly over bulk OUT. Disconnect deletes timers, unregisters mac80211, disables RX/TX, resets the USB device to allow later firmware upload, and releases hardware. Reset and PM paths stop USB transport, remember running state, and optionally resume/restores settings.

## State And Persistence
`struct plfxlc_usb` persists interface pointers, RX/TX state, per-station queues, timers, current round-robin station index, RX enabled flag, initialized flag, previous running state, and link-up status. RX URBs own coherent buffers while enabled. TX station flags track connected, FIFO-full, and heartbeat state. Firmware and USB configuration persist until reset or disconnect.

## Dependencies And Integration Points
This file integrates Linux USB core, mac80211 registration/unregistration, firmware helpers, chip control, and MAC TX/RX helpers. It is the module init/exit owner through `usb_register()`/`usb_deregister()`.

## Risks
`rx_urb_complete()` increments `submitted_urbs` twice in the retry log path, which can shorten retry allowance. `get_plfxlc_usb()` dereferences the result of `plfxlc_intf_to_hw()` through `plfxlc_usb_to_mac(pl)` after checking `pl`, but `pl` is derived from `hw`; PM suspend calls `plfxlc_usb_to_mac(pl)` before verifying `pl` is non-NULL, creating a NULL-risk path if no hw is attached. Async TX URBs use SKB data buffers without anchoring the URB in `tx->submitted`, so lifetime correctness depends on completion and mac80211 teardown ordering. FIFO status names appear inverted in logs versus flag behavior. Probe registers hw before firmware download; failed firmware download must unregister/release cleanly.

## Test Signals
Test probe/disconnect for X, XC, and XL IDs, missing firmware, USB reset, suspend/resume, bulk IN/OUT error injection, RX URB allocation failure, FIFO full/not-full status, connect/disconnect status, station queue cleanup timer, TX retry timer, queue stop/wake, and module unload/reload. KASAN and USB fault injection are especially useful for URB/SKB lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.h

## Purpose
This header declares the pureLiFi USB transport ABI, supported device IDs, endpoint IDs, firmware constants, RX/TX state structures, station queue state, timers, and public USB helper APIs.

## Important APIs, Types, And Functions
Definitions include USB vendor/product IDs for X/XC/XL, firmware buffer sizes and magic values, endpoint IDs `EP_DATA_IN` and `EP_DATA_OUT`, RX URB count, station FIFO/status message ids, station flag bits, `struct plfxlc_usb_rx`, `struct plf_station`, `struct plfxlc_firmware_file`, `struct plfxlc_usb_tx`, and `struct plfxlc_usb`. Inline helpers convert USB/interface pointers to `usb_device` and `ieee80211_hw`.

Public prototypes cover sync/async writes, TX completion, USB init/release, RX/TX enable/disable, hardware init, speed naming, firmware download, and metadata upload.

## Control Flow
The header itself has no major execution path, but its inline conversions are used by USB callbacks and chip/MAC helpers. Its structures drive RX URB allocation, station queue scheduling, and device probe state.

## State And Persistence
`struct plfxlc_usb` is embedded in `struct plfxlc_chip` and persists for the `ieee80211_hw` lifetime. It owns RX URB arrays, TX station queues, timers, interface references, flags, and link state. `struct plfxlc_firmware_file` is transient metadata for packed XL firmware parsing.

## Dependencies And Integration Points
Includes Linux completion/netdevice/spinlock/skbuff/USB headers and `intf.h`. It is included by chip, mac, firmware, and usb implementation files.

## Risks
The header declares `int plfxlc_usb_tx()` but this function is not implemented in the viewed source set, so callers would fail to link if introduced. `DEVICE_LIFI_XC` and `DEVICE_LIFI_XL` share value 1, which is fine if only informational but ambiguous if logic later distinguishes them. Host storage `PURELIFI_SERIAL_LEN` is 256 while firmware serial length in `intf.h` is 14. Timer and queue state must be initialized exactly once during probe.

## Test Signals
Compile/link coverage should catch stale prototypes. Runtime validation includes endpoint use, station queue flags, timer behavior, firmware file metadata handling, and correct USB ID matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Kconfig

## Purpose
This Kconfig file adds the Quantenna wireless vendor menu and conditionally includes the qtnfmac driver Kconfig.

## Important APIs, Types, And Functions
It defines `config WLAN_VENDOR_QUANTENNA` as a default-y boolean vendor selector and sources `drivers/net/wireless/quantenna/qtnfmac/Kconfig` when enabled.

## Control Flow
During kernel configuration, enabling the vendor selector exposes Quantenna FullMAC PCIe support options. The selector does not build code by itself.

## State And Persistence
The persistent configuration output is `CONFIG_WLAN_VENDOR_QUANTENNA` and any subordinate qtnfmac symbols.

## Dependencies And Integration Points
Integrated by the parent wireless Kconfig tree and delegates actual driver configuration to qtnfmac.

## Risks
Disabling the vendor gate hides all Quantenna driver options. Path drift in the sourced Kconfig would break menu traversal.

## Test Signals
Run Kconfig with the vendor enabled/disabled and verify qtnfmac options appear only under the enabled vendor menu.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Makefile

## Purpose
This Makefile descends into the Quantenna qtnfmac driver directory when the common qtnfmac symbol is enabled.

## Important APIs, Types, And Functions
The build rule is `obj-$(CONFIG_QTNFMAC) += qtnfmac/`.

## Control Flow
Kbuild includes `drivers/net/wireless/quantenna/qtnfmac/` in the build graph when `CONFIG_QTNFMAC` is built-in or modular.

## State And Persistence
No runtime state exists. The persistent effect is build graph membership for qtnfmac.

## Dependencies And Integration Points
Consumes `CONFIG_QTNFMAC` selected by transport-specific options such as `QTNFMAC_PCIE`.

## Risks
If `QTNFMAC_PCIE` selects `QTNFMAC` but this rule is wrong, neither the common nor PCIe modules build. Additional Quantenna drivers would need explicit rules.

## Test Signals
Build with `CONFIG_QTNFMAC_PCIE=m` and confirm both common and PCIe qtnfmac modules are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Kconfig

## Purpose
This Kconfig file defines the Quantenna FullMAC common symbol and PCIe transport option for QSR1000/QSR2000/QSR10g adapters.

## Important APIs, Types, And Functions
`config QTNFMAC` is a hidden tristate that depends on `QTNFMAC_PCIE` and mirrors the PCIe symbol's built-in/module state. `config QTNFMAC_PCIE` is the user-visible tristate, depends on `PCI` and `CFG80211`, selects `QTNFMAC`, `FW_LOADER`, and `CRC32`, and describes the two module outputs `qtnfmac.ko` and `qtnfmac_pcie.ko`.

## Control Flow
Selecting PCIe support enables the common qtnfmac core and PCIe transport build. The common symbol defaults to module or built-in according to the PCIe symbol.

## State And Persistence
The `.config` persists `CONFIG_QTNFMAC_PCIE` and derived `CONFIG_QTNFMAC`.

## Dependencies And Integration Points
Consumed by `qtnfmac/Makefile`, which splits common objects and PCIe-specific objects. Dependencies match the driver's cfg80211, PCI, firmware loader, and CRC usage.

## Risks
The common symbol depends on the PCIe symbol, so adding another bus requires revisiting dependency/default logic. Incorrect select/depend choices could expose build failures or omit firmware support.

## Test Signals
Kconfig tests should verify `QTNFMAC` follows `QTNFMAC_PCIE` for y/m, and that disabling PCI or CFG80211 hides PCIe support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Makefile

## Purpose
This Makefile builds the Quantenna qtnfmac common FullMAC driver and PCIe transport module.

## Important APIs, Types, And Functions
It adds include flags for the qtnfmac directory, builds `qtnfmac.o` from common objects (`core.o`, `commands.o`, `trans.o`, `cfg80211.o`, `event.o`, `util.o`, `qlink_util.o`), and builds `qtnfmac_pcie.o` from shared-memory IPC and PCIe platform objects. Debugfs support adds `debug.o` to the PCIe module when enabled.

## Control Flow
Kbuild links common cfg80211/command/event/transport functionality into the common module and hardware/transport-specific code into the PCIe module according to the relevant config symbols.

## State And Persistence
No runtime state exists. The file defines module composition and include path state.

## Dependencies And Integration Points
Driven by `CONFIG_QTNFMAC` and `CONFIG_QTNFMAC_PCIE`, and consumed by Kbuild under the Quantenna vendor directory.

## Risks
Common and bus-specific module boundaries must stay aligned with exported symbols. Missing a new common object can produce unresolved symbols in PCIe or incomplete cfg80211 behavior. Debugfs object is transport-specific here.

## Test Signals
Build both built-in and module configurations, with and without DEBUG_FS, and confirm common and PCIe modules link without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/bus.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/bus.h

## Purpose
This header defines the Quantenna qtnfmac bus abstraction shared by the common FullMAC core and hardware transports such as PCIe. It describes firmware state, host bus operations, global bus state, bus-private storage, locking wrappers, and attach/detach APIs.

## Important APIs, Types, And Functions
Key types are `struct qtnf_frame_meta_info`, `enum qtnf_fw_state`, `struct qtnf_bus_ops`, and `struct qtnf_bus`. Inline helpers include `qtnf_fw_is_up()`, `qtnf_fw_is_attached()`, `get_bus_priv()`, `qtnf_bus_preinit()`, `qtnf_bus_stop()`, `qtnf_bus_data_tx()`, `qtnf_bus_data_tx_timeout()`, `qtnf_bus_control_tx()`, `qtnf_bus_data_rx_start()`, `qtnf_bus_data_rx_stop()`, `qtnf_bus_lock()`, and `qtnf_bus_unlock()`. External common-layer APIs are `qtnf_core_attach()` and `qtnf_core_detach()`.

## Control Flow
Transport drivers allocate a `struct qtnf_bus` with trailing private data, fill `bus_ops`, and call common attach. Common code calls inline wrappers to preinitialize transport, send control and data frames, start/stop RX, and stop the bus. The firmware state enum gates operations such as attach/running/dead checks. `bus_lock` serializes command and event processing.

## State And Persistence
`struct qtnf_bus` persists device pointer, firmware state, chip ids, MAC pointers, QLINK transport, hardware info, mux NAPI/netdev, workqueues, firmware/event work items, debugfs directory, netdev notifier, hardware id, and bus-private tail storage. Firmware state persists as a host-side state machine reflecting device lifecycle.

## Dependencies And Integration Points
Includes Linux netdevice/workqueue APIs and qtnfmac `trans.h`/`core.h`. It is included by common cfg80211/core/command paths and PCIe transport code. `qtnf_frame_meta_info` defines optional per-frame metadata for host bus multiplexing.

## Risks
`get_bus_priv()` returns `&bus->bus_priv`, whose type is a pointer to the flexible array member rather than `bus->bus_priv`; callers must treat it carefully. Operation wrappers assume required bus_ops callbacks are non-NULL except preinit/stop. Firmware state transitions must be consistent across asynchronous work and bus stop. Lock misuse can deadlock command/event handling.

## Test Signals
Validate attach/detach, firmware boot/running/dead transitions, control and data TX through PCIe ops, RX start/stop, NAPI mux behavior, bus lock contention under scan/connect/event load, and bus-private access in transport code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/cfg80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/cfg80211.c

## Purpose
This file is the cfg80211 integration layer for the Quantenna qtnfmac FullMAC driver. It maps Linux wireless operations to QLINK firmware commands, registers and configures wiphys, manages virtual interfaces, AP/station/connect/scan/key/channel/DFS/power operations, handles regulatory updates, and exposes helper functions used by the common core.

## Important APIs, Types, And Functions
The central operation table is `qtn_cfg80211_ops`, which implements virtual interface add/change/delete, AP start/stop/change beacon, wiphy parameter updates, management frame registration and TX, station operations, key operations, scan, connect/disconnect/external auth, survey/channel queries, channel switch, radar detection, MAC ACL, power management, TX power, OWE updates, and optional PM/WoWLAN callbacks.

Important exported helpers are `qtnf_wiphy_allocate()`, `qtnf_wiphy_register()`, `qtnf_netdev_updown()`, `qtnf_virtual_intf_cleanup()`, `qtnf_cfg80211_vif_reset()`, `qtnf_band_init_rates()`, and `qtnf_band_setup_htvht_caps()` declared later in the file. Interface helpers include `qtnf_validate_iface_combinations()`, `qtnf_add_virtual_intf()`, `qtnf_change_virtual_intf()`, and `qtnf_del_virtual_intf()`.

## Control Flow
Wiphy allocation optionally disables unsupported ops based on hardware capabilities, allocates a wiphy with `struct qtnf_wmac` private data, and binds it to a platform or bus device. Registration fills thresholds, scan limits, management frame types, interface combinations, cipher suites, signal type, flags, DFS/scan dwell features, antenna counts, AP association limits, HT/VHT capability masks, permanent address, feature bits, WoWLAN, regulatory behavior, extended capabilities, firmware/hardware versions, and then calls `wiphy_register()`. After registration it applies a self-managed regdomain or regulatory hint when available.

Virtual interface add validates cfg80211 combinations plus qtnfmac repeater ordering rules, allocates a free VIF, initializes wireless_dev fields, sends firmware add-interface command, validates firmware-provided MAC, attaches a netdev, optionally notifies firmware of hardware bridge domain, and returns the wireless_dev. Change stops scans and sends change-interface command. Delete stops data queues/carrier, flushes high-priority TX queue/work, unregisters netdev, sends firmware delete, clears netdev/wdev state, and marks the VIF unspecified.

Operational callbacks are mostly command translations: AP start/stop and beacon IEs, management registration/TX, station/key/default-key changes, scan start with timeout work, connect/disconnect/external-auth, survey/channel queries, CSA, CAC/DFS, MAC ACL, PM, TX power, OWE, and WoWLAN. Several callbacks force scan completion before disruptive operations. Station dump consults local STA lists and asks firmware for live station info, deleting stale AP stations when firmware returns `-ENOENT`.

Regulatory notifier sends region and radar/offload configuration to firmware and refreshes band info for all registered bands. Cleanup helpers disconnect station VIFs, cancel scans, or notify cfg80211 of shutdown/disconnection.

## State And Persistence
Persistent state spans `struct qtnf_wmac` and its VIF array: interface type, netdev/wdev pointers, MAC/BSSID, station lists, generation, management frame bitmask, scan request and timeout work, regulatory domain, macinfo capabilities, and bus hardware info. Firmware owns actual AP/station/key/scan/channel/DFS/power state; this layer mirrors enough state to satisfy cfg80211 and netdev lifetimes.

## Dependencies And Integration Points
Depends on Linux cfg80211, netdevice, regulatory, workqueue, and netlink APIs; qtnfmac command functions in `commands.h`; core VIF/MAC helpers in `core.h`; bus hardware capability state in `bus.h`; and utility functions for DFS/offload policy. It is invoked from common core attach/register flows and by cfg80211 from userspace wireless requests.

## Risks
`qtnf_wiphy_allocate()` mutates the global/static `qtn_cfg80211_ops` table based on one bus's capabilities, which can affect later devices with different capabilities. Interface combination logic adds qtnfmac-specific repeater constraints beyond cfg80211 and can reject otherwise valid combinations. Many callbacks assume `wdev->netdev` exists and VIF state is initialized. Scan request state and timeout work must be canceled on every path that disrupts firmware scanning. Regulatory updates refresh band info after firmware notification and can leave stale host bands on partial failure. Because most operations are firmware-command wrappers, error propagation and host mirror cleanup must stay synchronized with firmware state.

## Test Signals
Validate wiphy registration for different capability sets, station and AP VIF add/change/delete, STA+AP repeater ordering, AP start/stop/beacon IE updates, management frame registration/TX, WPA/WPA2/802.11w keys, scan timeout/cancel, connect/disconnect including SAE external auth, station dump stale removal, survey/channel query, CSA, DFS CAC with and without DFS offload, MAC ACL, power-save, TX power, OWE, WoWLAN suspend/resume, regulatory notifier, and multi-device capability differences. cfg80211/mac80211_hwsim-style tests plus firmware command tracing are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/cfg80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/cfg80211.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/cfg80211.h

## Purpose
This header declares the public cfg80211-facing helper API for the Quantenna qtnfmac common driver.

## Important APIs, Types, And Functions
It declares `qtnf_wiphy_register()`, `qtnf_del_virtual_intf()`, `qtnf_cfg80211_vif_reset()`, `qtnf_band_init_rates()`, and `qtnf_band_setup_htvht_caps()`.

## Control Flow
The header has no execution path. Common core code includes it to allocate/register wiphy state, remove VIFs, reset cfg80211-facing VIF state, and initialize band rate/capability data.

## State And Persistence
The declared functions operate on persistent `struct qtnf_wmac`, `struct qtnf_vif`, `struct wiphy`, and `struct ieee80211_supported_band` state owned elsewhere.

## Dependencies And Integration Points
Includes cfg80211 and qtnfmac core definitions. It bridges `cfg80211.c` to common core, command, and bus attach logic.

## Risks
Any prototype drift against `cfg80211.c` or core callers breaks the common qtnfmac build. The API exposes destructive operations such as VIF delete/reset, so callers must hold appropriate rtnl/cfg80211 context as required by the implementation.

## Test Signals
Compile coverage for qtnfmac common and PCIe modules validates declarations. Runtime signals come from wiphy registration, VIF cleanup, band initialization, and reset flows during disconnect and firmware failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/cfg80211.h -->

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

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/fw.c

## Purpose

`fw.c` is the main firmware communication and firmware-offload implementation for `rtw88`. It handles C2H receive dispatch, H2C mailbox and packet commands, firmware debug dumping, rate-adaptation reports, beacon-filter notifications, coexistence commands, power-save/WoWLAN commands, reserved-page construction and download, firmware FIFO dumps, probe-request updates, scan offload, and scan channel-switch notifications.

## Important APIs, Types, and Functions

Public entry points include `rtw_fw_c2h_cmd_rx_irqsafe()`, `rtw_fw_c2h_cmd_handle()`, `rtw_fw_c2h_cmd_isr()`, `rtw_fw_send_general_info()`, `rtw_fw_send_phydm_info()`, `rtw_fw_do_iqk()`, `rtw_fw_inform_rfk_status()`, coexistence H2C helpers, `rtw_fw_send_rssi_info()`, `rtw_fw_send_ra_info()`, `rtw_fw_media_status_report()`, `rtw_fw_beacon_filter_config()`, WoW/LPS/NLO command helpers, reserved-page add/remove/download helpers, `rtw_fw_dump_fifo()`, `rtw_fw_update_pkt_probe_req()`, `rtw_fw_channel_switch()`, `rtw_fw_adaptivity()`, scan notify/offload helpers, and operating-channel backup/restore helpers.

The implementation revolves around protocol structures and macros from `fw.h`: `struct rtw_c2h_cmd`, `struct rtw_c2h_ra_rpt`, `struct rtw_h2c_cmd`, `struct rtw_rsvd_page`, reserved packet types, H2C command IDs, H2C packet subcommands, and field setters for little-endian firmware buffers.

## Control Flow

C2H handling has an IRQ-safe front half and a mutex-protected worker path. `rtw_fw_c2h_cmd_rx_irqsafe()` stores the packet offset in `skb->cb`, immediately handles BT MP responses, WLAN RF-on completion, and scan-density reports, and queues all other events to `rtwdev->c2h_queue` plus `c2h_work`. `rtw_fw_c2h_cmd_handle()` locks `rtwdev->mutex`, ignores events while the device is not running, and dispatches by C2H ID to TX reports, coexistence notifications, beacon-filter notifications, HALMAC extensions, RA reports, and adaptivity diagnostics.

H2C command flow supports two transports. Short register/mailbox commands use `rtw_fw_send_h2c_command()` or `rtw_fw_send_h2c_command_register()`, polling `REG_HMETFR` for a free mailbox, writing the extended word first, then the command word, and rotating `rtwdev->h2c.last_box_num`. Packet H2C commands use `rtw_fw_send_h2c_packet()`, stamp `rtwdev->h2c.seq`, and call `rtw_hci_write_data_h2c()`.

Reserved-page flow starts with per-vif lists created by `rtw_add_rsvd_page_bcn()`, `rtw_add_rsvd_page_sta()`, or `rtw_add_rsvd_page_pno()`. `rtw_fw_download_rsvd_page()` gathers active vif entries into the device build list, ensures the first page is a beacon or dummy page, creates skb contents through mac80211 helpers or local builders, optionally prepends TX descriptors, lays packets into page-aligned firmware buffer space, downloads the buffer through `rtw_fw_write_data_rsvd_page()`, then downloads the beacon alone again so the beacon's TX descriptor is correct.

Scan offload flow uses reserved H2C information pages. `rtw_hw_scan_start()` stops queues, leaves deep LPS, flushes queues, configures randomized or normal scan address state, and disables beacon BSSID filtering. `rtw_hw_scan_offload()` builds probe requests and channel lists, writes them to reserved pages, then sends an H2C scan-offload packet. Firmware C2H channel-switch notifications update the driver's current channel, stop or wake queues around off-channel work, notify coexistence of 2.4/5 GHz transitions, and manage beaconing. Scan status C2H completes the scan and reports abort status to mac80211.

## State and Persistence

Persistent driver state updated here includes `rtwdev->h2c.last_box_num`, `rtwdev->h2c.seq`, station RA report fields and AMSDU limits, `rtwdev->beacon_loss`, `dm_info->tx_rate`, `dm_info->scan_density`, LPS/WoW command-derived flags, reserved-page build locations, `rsvd_pkt->page`, `rsvd_pkt->tim_offset`, `rsvd_pkt->probe_req_size`, `rtwdev->scan_info` operating-channel fields, and temporary probe-page size. Firmware receives persistent command state for RA masks, RSSI, media status, beacon filtering, power mode, WoWLAN, NLO, packet locations, and scan offload.

Most H2C and reserved-page paths require `rtwdev->mutex`; several functions assert it. The C2H front half is designed for IRQ-safe contexts and defers most work. Reserved-page build lists are temporary and reset before each build, while per-vif reserved-page lists persist until interface removal.

## Dependencies and Integration Points

`fw.c` integrates with mac80211 skb constructors (`ieee80211_beacon_get_tim`, `ieee80211_pspoll_get`, `ieee80211_nullfunc_get`, `ieee80211_probereq_get`), HCI data paths, TX descriptor filling, security CAM backup, coexistence notification handling, power-save and WoW helpers, PHY/SAR/adaptivity state, firmware recovery, and core scan state. It is called from mac80211 callbacks in `mac80211.c`, MAC bring-up in `mac.c`, debugfs H2C and FIFO dump paths, and power-management paths.

## Risks

Firmware protocol packing is brittle. Every H2C field setter assumes the exact firmware ABI, little-endian layout, and packet length. A wrong bitfield, stale feature gate, or missing sequence update can silently break offloaded behavior. The code also has many hardware sequencing assumptions: mailbox free polling, reserved-page register backup/restore, beacon-valid polling, RX clock-gate toggling during FIFO dump, and queue stops around scan channel switches.

Reserved-page construction is size-sensitive. The first packet rule, page-margin math, chip page size, TX descriptor size, and reserved driver page count must all align. Oversized probe requests or too many PNO/scan entries fail, and errors during build must free all temporary skbs. `rtw_fw_dump_check_size()` appears weak for TX/RX FIFO bounds because it compares `start_addr + size` with a base page address rather than a FIFO length, so callers still need conservative inputs.

Concurrency risks center on firmware events racing stop/restart/scanning. The worker path drops C2H while not running, scan abort and completion share `scan_info.scanning_vif`, and debugfs can inject H2C commands outside normal typed call sites.

## Test Signals

Validation should cover C2H dispatch for RA reports, TX reports, BT/coex info, beacon loss/signal events, scan density, scan status, and channel switch notifications. H2C tests should verify mailbox rotation, timeout logging, packet sequence increments, and feature-gated commands on firmware versions with and without beacon filter or scan offload. Reserved-page tests should exercise station, AP, PNO, LPS page, and beacon update paths, including page overflow and skb allocation failures. Hardware scan tests should cover active/passive/radar channels, randomized addresses, AP-active beacon preservation, aborts, firmware error codes, and queue stop/wake behavior.

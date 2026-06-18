# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/core.c

## Purpose

`core.c` is the shared core of the Realtek `rtl8xxxu` USB mac80211 driver. It binds USB device IDs to chip-specific `rtl8xxxu_fileops`, owns the generic USB control/bulk/interrupt transport, loads firmware, reads EFUSE data, initializes MAC/PHY/RF state, registers the `ieee80211_hw`, and implements the mac80211 callbacks used for station/AP operation, channel changes, encryption keys, TX/RX, aggregation, beaconing, rate reporting, and teardown.

The file supports multiple related 2.4 GHz Realtek USB chip families through generic helpers plus chip-specific hooks supplied by sibling files such as `8723a.c`, `8723b.c`, `8188e.c`, `8192e.c`, `8192f.c`, and `8710b.c`. It also declares the module parameters `debug`, `dma_aggregation`, `dma_agg_timeout`, and `dma_agg_pages`, and advertises the firmware blobs required by supported chips.

## Important APIs, Types, and Tables

- Module and bus entry points: `rtl8xxxu_driver`, `dev_table`, `rtl8xxxu_probe()`, and `rtl8xxxu_disconnect()`.
- mac80211 entry points: `rtl8xxxu_ops` wires `.tx`, `.start`, `.stop`, `.add_interface`, `.remove_interface`, `.config`, `.conf_tx`, `.bss_info_changed`, `.start_ap`, `.configure_filter`, `.set_key`, `.ampdu_action`, `.sta_add`, `.sta_remove`, `.sta_statistics`, `.get_antenna`, `.set_tim`, and software scan callbacks.
- Register access API: `rtl8xxxu_read8/16/32()`, `rtl8xxxu_write8/16/32()`, set/clear/mask helpers, `rtl8xxxu_read_rfreg()`, `rtl8xxxu_write_rfreg()`, and `rtl8xxxu_write_rfreg_mask()`. These serialize shared USB control-buffer use with `usb_buf_mutex`; RTL8710B low register addresses are remapped through the 0x8000 region.
- Firmware/H2C APIs: `rtl8xxxu_load_firmware()`, `rtl8xxxu_download_firmware()`, `rtl8xxxu_start_firmware()`, `rtl8xxxu_reset_8051()`, `rtl8xxxu_firmware_self_reset()`, `rtl8xxxu_gen1_h2c_cmd()`, and `rtl8xxxu_gen2_h2c_cmd()`.
- EFUSE/debugfs APIs: `rtl8xxxu_read_efuse8()`, `rtl8xxxu_read_efuse()`, `rtl8xxxu_dump_efuse()`, `read_file_efuse()`, and `rtl8xxxu_debugfs_init()`.
- Initialization helpers: `rtl8xxxu_init_device()`, `rtl8xxxu_init_mac()`, `rtl8xxxu_init_phy_regs()`, `rtl8xxxu_init_phy_bb()`, `rtl8xxxu_init_phy_rf()`, `rtl8xxxu_init_llt_table()`, `rtl8xxxu_auto_llt_table()`, queue priority/reserved-page setup, burst/aggregation setup, and gen1/gen2 USB quirks.
- RF/channel/power/calibration helpers: gen1/gen2 channel-to-group and channel configuration, gen1 TX-power programming, RF enable/disable paths, LC calibration, IQK backup/restore, IQK matrix fill, and similarity comparison helpers.
- Data path helpers: TX descriptor fillers for v1/v2/v3 formats, TX descriptor checksum generation, URB pools and anchors, RX descriptor parsers for 16-byte and 24-byte descriptors, PHY-stat parsers for legacy and Jaguar2 formats, C2H command handling, RSSI update, and watchdog-driven rate/CFO maintenance.
- Key state types come from `rtl8xxxu.h`: `struct rtl8xxxu_priv`, `struct rtl8xxxu_fileops`, `struct rtl8xxxu_vif`, `struct rtl8xxxu_sta_info`, `struct rtl8xxxu_rx_urb`, and `struct rtl8xxxu_tx_urb`.
- Static hardware tables include 2 GHz channel/rate declarations, gen1 PHY init arrays, standard/high-PA AGC tables, and RF path register maps.

## Control Flow

Probe starts in `rtl8xxxu_probe()`. It classifies tested vs untested USB IDs, allocates `ieee80211_hw` with private `rtl8xxxu_priv`, installs the `driver_info` chip `fops`, initializes mutexes, locks, lists, work items, SKB queues, and interface data, then parses USB endpoints. The chip-specific `identify_chip()`, `read_efuse()`, `parse_efuse()`, and `load_firmware()` hooks populate chip identity, EFUSE-derived MAC/power/RF data, and firmware bytes. `rtl8xxxu_init_device()` then powers the chip, configures queue pages and endpoint-to-queue priority, downloads and starts firmware with retry, initializes MAC/PHY/RF, programs RX filters, EDCA, beacon timing, aggregation, CAM invalidation, default TX power, calibrations, thermal/CFO tracking, and reserved MAC IDs. Probe finally configures wiphy capabilities, HT support, queue count, interface modes, headroom, feature flags, registers mac80211, registers LED support, and exposes EFUSE in debugfs.

Runtime start is separate from probe. `rtl8xxxu_start()` enables RF, submits the optional interrupt URB, allocates a pool of TX URBs, clears RX shutdown, submits RX URBs, starts the rate/CFO watchdog, opens RX filter maps, and sets initial gain. `rtl8xxxu_stop()` pauses TX, blocks RX filters, marks RX shutdown, kills anchored RX/TX/interrupt URBs, disables RF and interrupts, cancels C2H/rate/beacon work, and frees pending RX/TX resources.

TX enters `rtl8xxxu_tx()`. The function validates SKB headroom and length, obtains a free TX URB with queue stop/wake watermarks, selects the Realtek queue from the 802.11 frame class and AC mapping, pushes a chip-sized descriptor, fills packet size, queue, multicast and security flags, optionally starts BA aggregation for QoS HT data, derives SGI/preamble/RTS/CTS settings, delegates chip descriptor details to `fops->fill_txdesc()`, calculates the descriptor checksum, anchors and submits a USB bulk URB, and reports status in `rtl8xxxu_tx_complete()`.

RX completion appends the actual USB length to the SKB and delegates descriptor parsing through `fops->parse_rx_desc()`. `rtl8xxxu_parse_rxdesc16()` and `rtl8xxxu_parse_rxdesc24()` handle aggregated buffers by cloning the SKB when another descriptor follows, converting descriptor fields from little endian, pulling descriptor/PHY/status prefixes, trimming to packet length, dispatching C2H reports, or filling `ieee80211_rx_status` with PHY signal, rate, HT, bandwidth, decryption, CRC, mactime, frequency, and band before `ieee80211_rx_irqsafe()`. Completed RX URBs are queued and resubmitted by `rtl8xxxu_rx_urb_work()` so allocation failures can be retried without dropping the URB object.

mac80211 state changes program hardware registers and firmware mailboxes. `rtl8xxxu_add_interface()` assigns one of two hardware ports, handles STA/AP beacon register setup, and writes MAC/link type. `rtl8xxxu_bss_info_changed()` handles association, BSSID, basic rates, ERP slot/preamble, and beacon state, including firmware connect reports and rate-mask setup. `rtl8xxxu_config()` handles channel changes by updating TX power and chip channel registers. `rtl8xxxu_conf_tx()` programs EDCA and ACM bits. `rtl8xxxu_set_key()` allocates CAM entries and writes WEP/TKIP/CCMP material. `rtl8xxxu_ampdu_action()` tracks BA state and AMPDU limits. AP beacon updates are delayed work items that fetch a mac80211 beacon frame and send it through the normal TX path.

## State and Persistence Behavior

Most state is volatile driver and device state under `struct rtl8xxxu_priv`. Persistent hardware inputs are EFUSE/EEPROM contents and firmware files; the driver copies EFUSE into `priv->efuse_wifi.raw`, parses it into MAC address, RF paths, chip flags, power indices, crystal cap, and feature flags, and exposes the raw EFUSE map via debugfs. Firmware is requested from the kernel firmware loader, copied into `priv->fw_data`, downloaded page by page over USB control writes, and freed at disconnect or probe failure.

Runtime state includes endpoint maps, USB pipe handles, URB anchors, TX free-list watermarks, RX pending list, two virtual interface pointers, MAC ID and CAM bitmaps, station RSSI EWMA and rate level, C2H command queue, BT coexistence status, rate-report cache, CFO tracking, LED registration state, and calibration backups. The driver persists security keys only in hardware CAM until disabled, stop, power off, or device removal. Calibration and CFO adjustments write hardware registers and are held in memory for recovery or future watchdog decisions, not across module unload or unplug.

Concurrency is split by subsystem: USB control transfer scratch storage is protected by `usb_buf_mutex`; firmware H2C mailbox allocation by `h2c_mutex`; station iteration and MAC ID updates by `sta_mutex`; TX/RX URB lists by spinlocks; RX/C2H/beacon/rate work runs from workqueues. USB anchors provide bulk cancellation at stop/disconnect boundaries.

## Dependencies and Integration Points

This file integrates with Linux USB core (`usb_control_msg`, endpoint descriptors, URBs, anchors, USB device IDs), mac80211/cfg80211 (`ieee80211_hw`, `ieee80211_ops`, channel/rate/HT capabilities, SKB control blocks, station/vif private data), firmware loader (`request_firmware()`), debugfs, LED class, kernel workqueues, SKB allocation, bitmaps, RCU station lookup, and device logging. Register constants, descriptor layouts, EFUSE layouts, H2C/C2H structs, and `rtl8xxxu_priv` are defined in `regs.h` and `rtl8xxxu.h`.

Chip-specific files provide `rtl8xxxu_fileops` implementations for identifying chips, parsing EFUSE, selecting firmware, power sequencing, RF/PHY init, descriptor formats, RX PHY stats, aggregation, rate-mask handling, CCK RSSI conversion, LEDs, and crystal-cap control. `dev_table` binds USB IDs to these fops. Firmware names declared by `MODULE_FIRMWARE()` must match the chip-specific `load_firmware()` paths.

The driver advertises a 2.4 GHz band, HT capabilities derived from RF path count, station and optional AP modes, optional concurrent STA/AP combinations, mac80211-managed channel contexts via emulation helpers, firmware or driver rate control depending on chip, fast xmit, AMPDU, management frame protection, CQM RSSI list support, and optional debugfs EFUSE inspection.

## Risks and Edge Cases

- Hardware sequencing is fragile. Many initialization and calibration writes are undocumented or vendor-derived; changing order, delays, masks, or chip conditionals can break only one chip/cut/vendor combination.
- Firmware download/start failures return `-EAGAIN` or timeout after polling checksum/init bits. Bad firmware signatures, missing blobs, wrong fops-to-USB-ID mapping, or incorrect page sizes can leave the device unusable.
- USB register access uses a shared union buffer and assumes synchronous control messages. Missing locking or incorrect RTL8710B address remapping would corrupt reads/writes.
- RX aggregation parsing depends on exact descriptor size, alignment roundup, packet count, and SKB clone boundaries. Off-by-one errors risk frame corruption, leaks, or passing malformed packets to mac80211.
- TX completion reports ACK solely from URB status for many frames, while firmware TX reports are chip-dependent. Rate-control and user-visible TX status can be misleading if report handling diverges from hardware behavior.
- Queue and URB watermarks stop/wake all mac80211 queues. Leaks in the free-list path, failed submit cleanup, or stop racing with RX requeue can stall traffic.
- Security CAM handling supports limited key indexes and cipher set; AP group keys reuse `rtlvif->hw_key_idx` for broadcast/multicast descriptor IDs. CAM bitmap or key-disable mistakes can break encryption or leak stale keys.
- Dual-port/concurrent mode has special port switching and comments noting assumptions about NULL vifs. Future interface combinations could violate those assumptions.
- BT coexistence and CFO tracking are heuristic and partly TODO-driven. Incorrect C2H interpretation or crystal-cap changes can degrade WiFi/BT operation or frequency stability.
- Module parameters for DMA aggregation can expose aggregation parser bugs and have a suspicious branch where `dma_agg_pages` validation assigns `timeout = page_thresh`, so parameter behavior deserves care.

## Test Signals

- Build coverage for representative configs with and without `CONFIG_RTL8XXXU_UNTESTED`, plus all chip fops objects referenced by `dev_table`.
- Probe logs: tested/untested notice, endpoint parse, chip info, EFUSE read/parse, firmware revision/signature, firmware checksum/init success, and successful `ieee80211_register_hw()`.
- Device smoke tests for supported USB IDs: module load/unload, unplug during traffic, suspend-like stop/start paths via interface down/up, and disconnect cleanup without URB or workqueue warnings.
- mac80211 behavior: scan, associate as STA, DHCP/traffic, channel changes for 20 MHz and 40 MHz, AP start/stop, beacon updates, CSA countdown, two-interface STA/AP or STA/STA combinations where supported.
- Data-path validation: sustained RX/TX, large SKBs rejected cleanly, aggregation on/off via `dma_aggregation`, BA session start/stop per TID, queue stop/wake under TX pressure, and no RX descriptor parse errors under aggregated USB buffers.
- Security tests for WEP/TKIP/CCMP setup and teardown, pairwise and group keys, AP broadcast/multicast traffic, and CAM reuse after key removal.
- Firmware communication signals: H2C mailbox busy handling, connect/rate/RSSI reports, C2H RA reports, RTL8188E TX report handling, and RTL8723B BT-info coexistence events.
- RF quality signals: RSSI values, station `txrate` statistics, watchdog rate-mask changes, CFO tracking changes, LC/IQ calibration warnings, thermal meter programming, and expected antenna count reporting.

# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/ipw2200.c lines 1-9592

## Scope

This chunk covers the first and largest part of the Intel PRO/Wireless 2200/2915 Linux driver implementation. It starts with module metadata, feature-gated version strings, module parameters, supported rates, QoS defaults, register-access helpers, sysfs/debug attributes, LED and RF-kill control, interrupt and host-command handling, EEPROM access, firmware and microcode loading, DMA queue setup, scan/association/roaming logic, RX packet processing, security/QoS helpers, and most Wireless Extensions handlers through `ipw_wx_get_powermode()`.

The file continues after this chunk. The next chunk starts at `ipw_wx_set_wireless_mode()` on line 9593, so final whole-file research must add the remaining private WEXT handlers, netdev/ethtool operations, PCI probe/remove, suspend/resume, geo tables, device registration, and module parameter declarations.

## Purpose

The visible code is the runtime core of the `ipw2200` PCI wireless driver. It translates Linux network, Wireless Extensions, sysfs, firmware-loader, DMA, and libipw callbacks into the low-level command and memory transactions expected by Intel 2200BG/2915ABG firmware. It owns most state transitions for bringing the card up, loading the correct firmware image for infrastructure, ad-hoc, or monitor mode, scanning channels, selecting a network, associating or roaming, processing firmware notifications, and delivering received 802.11 frames to libipw or monitor/promiscuous devices.

The implementation is firmware-driven: the host driver configures shared SRAM, DMA descriptors, command queues, and firmware command payloads, then reacts to firmware interrupts and notifications. Much of the policy in this chunk exists to avoid firmware crashes by validating channels, dwell times, queue state, association mode, and power/radio state before issuing commands.

## Dependencies

The chunk includes Linux scheduler/allocation and cfg80211 WEXT glue headers plus the driver-local `ipw2200.h` and `ipw.h`. It depends heavily on:

- PCI/MMIO helpers: `readb()`, `readl()`, `writeb()`, `writel()`, `memcpy_toio()`, coherent DMA, DMA pools, and single-buffer DMA mapping.
- Firmware loading: `request_firmware()` and `release_firmware()` for `ipw2200-bss.fw`, `ipw2200-ibss.fw`, and optional `ipw2200-sniffer.fw`.
- Kernel work scheduling: `work_struct`, `delayed_work`, tasklets, wait queues, jiffies, spinlocks, and mutexes.
- Wireless Extensions/libipw: `struct libipw_device`, `struct libipw_network`, scan/rate/security/QoS helpers, `libipw_rx()`, `libipw_rx_mgt()`, and `libipw_wx_*()` wrappers.
- cfg80211 rfkill state propagation through `wiphy_rfkill_set_hw_state()`.
- Header-defined hardware contracts from `ipw2200.h`: register offsets, status/config bits, host command IDs, DMA descriptor formats, RX packet formats, association/sys_config structures, ordinal tables, security constants, and queue sizes.

## Important APIs, Types, and Functions

### Module Configuration and Rate Tables

Lines 27-99 build `IPW2200_VERSION` from compile-time feature suffixes and define module-global defaults such as `associate`, `auto_create`, `led_support`, `disable`, `bt_coexist`, `hwcrypto`, `roaming`, `antenna`, `default_channel`, and `network_mode`. `ipw2200_rates[]` exposes 802.11b/g/a bitrates to the later wiphy/libipw setup, split by `ipw2200_a_rates` and `ipw2200_bg_rates`.

When `CONFIG_IPW2200_QOS` is enabled, lines 130-185 define default WME/QoS parameter sets for OFDM and CCK, plus a priority-to-hardware-queue mapping. These defaults feed association-time QoS activation and TX queue selection.

### Register and Memory Access

The direct helpers `_ipw_write8()`, `_ipw_write16()`, `_ipw_write32()`, `_ipw_read8()`, and `_ipw_read32()` access the low 4 KiB BAR area. The indirect helpers `_ipw_write_reg8()`, `_ipw_write_reg16()`, `_ipw_write_reg32()`, `_ipw_read_reg8()`, `_ipw_read_reg32()`, `_ipw_read_indirect()`, and `_ipw_write_indirect()` program `IPW_INDIRECT_ADDR`, `IPW_INDIRECT_DATA`, `IPW_AUTOINC_ADDR`, and `IPW_AUTOINC_DATA` to reach SRAM/register space above the direct window.

The public macro wrappers add debug logging. `_ipw_read_indirect()` and `_ipw_write_indirect()` handle unaligned starts, dword middle runs, and trailing bytes. These helpers are foundational for EEPROM SRAM transfer, firmware DMA control blocks, ordinals, error logs, RX frame descriptors, and firmware register programming.

### Interrupts, Status, and Host Commands

`__ipw_enable_interrupts()`, `__ipw_disable_interrupts()`, `ipw_enable_interrupts()`, and `ipw_disable_interrupts()` maintain `STATUS_INT_ENABLED` under `priv->irq_lock` and write `IPW_INTA_MASK_R`.

`ipw_irq_tasklet()` is the main deferred interrupt handler for lines 1916-2073. It reads and masks interrupt status, merges cached ISR bits, then handles RX transfer, command completion, TX queue completion, RF-kill completion, firmware fatal errors, parity errors, and miscellaneous notification bits. Fatal firmware errors capture `priv->error`, notify userspace about lost association when needed, clear `STATUS_INIT`/`STATUS_HCMD_ACTIVE`, wake waiters, and schedule `adapter_restart`.

`__ipw_send_cmd()` serializes host commands via `STATUS_HCMD_ACTIVE`, writes a command TFD into the command TX queue through `ipw_queue_tx_hcmd()`, waits on `wait_command_queue` for completion, records optional command logs, and rejects commands after RF-kill. Convenience wrappers send SSID, system config, adapter address, scan, association, supported rates, power, retry, RTS/fragmentation, card-disable, TX-power, RSN, QoS, and other firmware commands.

### Debug, Sysfs, and Error Capture

`snprint_line()`, `printk_buf()`, and `snprintk_buf()` format hex dumps. `ipw_get_ordinal()` reads firmware ordinal tables 0, 1, and 2 after `ipw_init_ordinals()` discovers their addresses. Ordinals are used for firmware statistics such as microcode version, RTC, missed beacons, CRC errors, TX failures, and current TX rate.

The chunk defines sysfs attributes for debug level, event logs, firmware error logs, command logs, optional radiotap interface control, scan age, LED enablement, raw status/config, NIC type, ucode version, RTC, EEPROM delay, selected indirect/direct registers, RF-kill, speed scan channels, network stats, and channel listings. Many debug attributes read or write device registers directly, so they are diagnostic rather than pure metadata.

`ipw_alloc_error_log()` snapshots firmware error and event logs into `struct ipw_fw_error`; `ipw_dump_error_log()` emits the decoded failure records.

### LED and RF-kill State

The LED code stores per-NIC LED masks in `priv->led_*`, toggles the `IPW_EVENT_REG`, and schedules delayed link/activity work for blink behavior. `ipw_led_init()` selects LED wiring from EEPROM NIC type and handles reversed LED mappings on type 1 cards. `ipw_led_shutdown()` cancels delayed LED work and turns LEDs off.

`rf_kill_active()` reads a hardware GPIO-ish register bit, updates `STATUS_RF_KILL_HW`, and informs cfg80211 rfkill. `ipw_radio_kill_sw()` toggles `STATUS_RF_KILL_SW`, cancels scans, schedules device down/up work, and handles the case where software tries to re-enable the radio while hardware RF-kill remains active.

### EEPROM and Firmware Loading

The EEPROM helpers bit-bang a Microwire-compatible EEPROM through `FW_MEM_REG_EEPROM_ACCESS`. `ipw_read_eeprom()` reads 128 words into `priv->eeprom`, `eeprom_parse_mac()` extracts the MAC address, and `ipw_eeprom_init_sram()` either copies a valid EEPROM image into SRAM or asks firmware to load it.

Firmware load uses `struct ipw_fw` with boot, ucode, and runtime firmware sizes. `ipw_get_fw()` validates the firmware blob. `ipw_load()` chooses the image by `iw_mode`, allocates/reset RX queues, stops and resets the NIC, loads boot firmware by DMA, starts the NIC, waits for initialization, loads microcode via DINO control registers, loads runtime firmware by DMA, initializes queues, retries on parity errors, reads EEPROM, enables interrupts, replenishes RX buffers, and acknowledges pending interrupts.

DMA firmware loading is built from `ipw_fw_dma_enable()`, `ipw_fw_dma_add_command_block()`, `ipw_fw_dma_add_buffer()`, `ipw_fw_dma_kick()`, and `ipw_fw_dma_wait()`. Command blocks are written to shared SRAM and checked by polling the current command-block index; timeout dumps DMA state and aborts.

### DMA Queues

TX queues are circular descriptor rings represented by `struct clx2_tx_queue` and `struct clx2_queue`. `ipw_queue_tx_init()` allocates a coherent TFD ring and per-entry `txb` array; `ipw_queue_init()` writes ring base/size/read/write registers and sets high/low watermarks. `ipw_queue_tx_reclaim()` follows the hardware read pointer, unmaps/free data TFD chunks with `ipw_queue_tx_free_tfd()`, counts TX packets, and wakes the netdev queue when space recovers.

RX queues are preallocated `struct ipw_rx_mem_buffer` pools. `ipw_rx_queue_alloc()` seeds all buffers into `rx_used`; `ipw_rx_queue_replenish()` allocates SKBs and DMA maps them; `ipw_rx_queue_restock()` writes DMA addresses into `IPW_RFDS_TABLE_LOWER` and advances the firmware write index. `ipw_rx_queue_space()` intentionally reserves two slots to distinguish full from empty.

### Scan, Association, Roaming, and Network Selection

`ipw_add_scan_channels()` builds grouped A/B/G scan channel lists from libipw geo data, respecting passive-only flags, current association channel, and optional speed-scan lists. `ipw_request_scan_helper()` serializes active, passive, and direct scans, queues concurrent scan requests in status bits, rejects scans while uninitialized/exiting/RF-killed, sends direct SSID commands when needed, schedules the scan watchdog, and marks `STATUS_SCANNING`.

`ipw_rx_notification()` is the firmware notification dispatcher. Association/authentication notifications update `STATUS_AUTH`, `STATUS_ASSOCIATING`, `STATUS_ASSOCIATED`, and `STATUS_DISASSOCIATING`, schedule link work, trigger ad-hoc checks, and pass association responses into libipw for QoS when configured. Scan completion clears scan bits, wakes waiters, handles queued direct/background/roam scans, schedules association or roam work, and emits delayed WEXT scan events. Beacon-missing notifications feed `ipw_handle_missed_beacon()`, which escalates from waiting to roaming scan to disassociation.

`ipw_best_network()` and `ipw_find_adhoc_network()` filter candidates by mode/capability, ESSID/BSSID/channel locks, privacy compatibility, scan age, rate compatibility, valid channel/mode, signal strength, and recent association attempts. `ipw_adhoc_create()` synthesizes a new IBSS network with a locally administered random BSSID when static ESSID/channel and auto-create permit it. `ipw_associate_network()` fills `priv->assoc_request`, sends SSID/rates/sys_config/sensitivity/QoS commands, updates `priv->channel`, `priv->bssid`, `priv->assoc_network`, and status bits before sending `IPW_CMD_ASSOCIATE`.

`ipw_roam()` implements a two-pass roam: first find a better AP and quiet-disassociate, then after disassociation associate to the saved target. `ipw_associate()` starts ordinary association when not in monitor, not already associated/associating, initialized, not scanning, and policy permits auto or static association.

### RX Data Path

`ipw_rx()` drains RX descriptors from `priv->rxq->read` to the firmware read index. For `RX_FRAME_TYPE`, it builds `struct libipw_rx_stats`, updates packet counters and RSSI averages, optionally clones packets for a promiscuous radiotap side interface, handles monitor mode, filters packets with `is_network_packet()`, rejects too-short frames, and dispatches management/data frames. For `RX_HOST_NOTIFICATION_TYPE`, it calls `ipw_rx_notification()`.

Management frames go to `libipw_rx_mgt()` and can update the ad-hoc station table or emit raw network-stat packets when `CFG_NET_STATS` is enabled. Data frames pass duplicate suppression via `is_duplicate_packet()` and then `ipw_handle_data_packet()`, which strips hardware-decryption artifacts when host decrypt is disabled and hands the skb to `libipw_rx()`. Optional radiotap monitor and promiscuous handlers prepend `struct ipw_rt_hdr` and translate channel, rate, antenna, signal, and noise metadata.

### Security and QoS

Security helpers send WEP/TKIP/CCMP keys to firmware and adjust host/hardware encrypt/decrypt flags. `ipw_wx_set_auth()`, `ipw_wx_set_encodeext()`, and `ipw_wx_set_encode()` bridge WEXT WPA/auth/cipher/key settings into libipw state, firmware RSN capabilities, and hardware crypto policy. TKIP is partially hardware-assisted: MIC handling still requires host processing.

QoS code, when compiled in, parses QoS data from probe responses/beacons, activates firmware QoS parameters, sends WME information elements, maps skb priority to one of four TX queues, applies no-ack policy, and schedules QoS reconfiguration when AP parameter counts change.

### Wireless Extensions in This Chunk

The chunk implements WEXT handlers through `ipw_wx_get_powermode()`: name, WPA IE, auth, encodeext, MLME, frequency/channel, mode, range, AP BSSID, ESSID, nick, sensitivity thresholds, bitrate/fixed-rate mask, RTS, TX power/RF kill, fragmentation, retry limits, scan start/results, WEP encode, power management, and private power-mode string reporting. Many setters trigger disassociation/reassociation or adapter restart because firmware mode and association parameters are not hot-swapped in place.

## Control Flow

The driver bring-up path visible in this chunk is:

1. Reset module/default runtime state with `ipw_sw_reset()`.
2. `ipw_load()` selects firmware by mode and requests it from userspace.
3. The NIC is stopped/reset, SRAM is zeroed, boot firmware is DMA loaded, the NIC is started, and firmware initialization is polled.
4. Microcode is loaded through DINO registers and verified by an alive response.
5. Runtime firmware is DMA loaded, queues are initialized, firmware initialization is polled again, EEPROM is read/copied to SRAM, interrupts are enabled, and RX buffers are replenished.
6. Work items later issue scans, associations, QoS activation, stats gathering, RF-kill polling, LED transitions, and adapter restarts.

The steady-state interrupt flow is:

1. The ISR, defined later, schedules `ipw_irq_tasklet()`.
2. The tasklet reads interrupt causes and processes RX, TX reclaim, command completion, RF kill, fatal errors, and parity.
3. RX frames are drained by `ipw_rx()`, which either processes 802.11 frames or dispatches firmware notifications.
4. Firmware scan/association/beacon notifications schedule process-context work for association, roaming, scan continuation, link up/down, or restart.
5. Host commands complete by reclaiming the command queue, clearing `STATUS_HCMD_ACTIVE`, and waking `__ipw_send_cmd()` waiters.

The scan/association policy flow is:

1. WEXT, background scan, missed beacon, or monitor mode schedules a scan work item.
2. `ipw_request_scan_helper()` builds a firmware scan request and marks `STATUS_SCANNING`.
3. Scan completion notification clears scan state, emits WEXT events, and schedules association or roaming if appropriate.
4. `ipw_associate()` filters known networks or creates an IBSS network, then `ipw_associate_network()` programs firmware association state.
5. Association/auth notifications update driver state and schedule link work. Missed beacons can trigger roam scans or disassociation.

## State and Persistence Behavior

The central persistent in-memory state is `struct ipw_priv`, defined in `ipw2200.h`, with status/config bitfields, locks, work items, `struct libipw_device`, PCI/MMIO base, RX/TX rings, firmware error log, command log, EEPROM copy, firmware ordinal table addresses, scan/association parameters, rates, security settings, QoS settings, link statistics, LED masks, RF-kill status, and optional monitor/promiscuous devices.

State persistence is mostly device and kernel-memory persistence, not filesystem persistence:

- Module parameters initialize `priv->config`, `priv->ieee` mode/band/modulation, thresholds, power, QoS, LED, crypto, association, and static channel behavior.
- EEPROM contents are cached in `priv->eeprom` and optionally mirrored into device SRAM for firmware use.
- Firmware command state lives in `priv->assoc_request`, `priv->sys_config`, `priv->rates`, command rings, RX/TX rings, and device SRAM/registers.
- Error and event logs persist in `priv->error` until cleared through sysfs.
- Scan results and known networks are maintained by libipw network lists, with ad-hoc helpers moving entries between active and free lists.
- Link quality and stats use rolling averages and ordinal deltas retained across periodic `ipw_gather_stats()` runs.
- Under `CONFIG_PM`, the raw firmware pointer and `fw_loaded` are static globals reused across suspend/resume paths visible in later chunks.

Concurrency is guarded by a mix of `priv->mutex` for process-context operations, `priv->lock` for device/status updates, `priv->irq_lock` for interrupt mask/status, `priv->ieee->lock` for network lists, and `rxq->lock` for RX buffer pools.

## Integration Points

This chunk integrates with:

- Linux PCI/netdev lifecycle implemented later in the file; those paths allocate `struct ipw_priv`, register devices, call `ipw_sw_reset()`, `ipw_load()`, `ipw_up()`, `ipw_down()`, and install WEXT handlers.
- Firmware files declared by `MODULE_FIRMWARE()` and loaded by `request_firmware()`.
- libipw for scan result storage, 802.11 frame decapsulation, management frame parsing, security state, WEXT encode/scan helpers, geo/channel validation, and QoS data carried in `struct libipw_network`.
- cfg80211 WEXT/rfkill compatibility through `cfg80211-wext.h` and `wiphy_rfkill_set_hw_state()`.
- Linux wireless tools and wpa_supplicant through WEXT handlers such as `SIOCSIWAUTH`, `SIOCSIWGENIE`, `SIOCSIWENCODEEXT`, `SIOCSIWSCAN`, `SIOCSIWFREQ`, `SIOCSIWMODE`, and private power-mode controls.
- Optional compile-time features: monitor mode, radiotap, promiscuous side interface, QoS, debug logging, and PM firmware caching.
- Hardware registers and shared SRAM contracts for IPW command queues, RX descriptor table, DMA boot loader, DINO microcode path, EEPROM access, event/error logs, LED GPIO/event bits, and ordinal tables.

## Risks and Edge Cases

- The chunk contains many direct register and SRAM writes; wrong ordering around reset, firmware DMA, queue initialization, or interrupt enablement can wedge the device or produce firmware fatal errors.
- `__ipw_send_cmd()` depends on a single `STATUS_HCMD_ACTIVE` command slot and interrupt-driven completion. Lost interrupts, RF-kill transitions, or queue corruption can time out commands and force restart paths.
- Several sysfs/debug attributes expose raw indirect/direct register writes. They are useful for diagnostics but can corrupt device state if used carelessly.
- Firmware blob validation checks aggregate size but the DMA loader assumes chunk headers and lengths inside the firmware image are coherent. Malformed firmware can trip `BUG_ON()` limits for command block counts.
- RX/TX DMA handling is sensitive to ring index sanity. The code guards TX hardware read index range and RX null buffers, but stale DMA mappings or descriptor count bugs can still corrupt networking or leak buffers.
- Wireless mode changes free cached firmware and schedule adapter restart. Races with pending scans, association, or RF-kill work are mitigated by mutexes/status bits but remain high-risk areas.
- Scan dwell-time logic carries firmware-specific workarounds; passive scans while associated are capped below beacon interval to avoid silent firmware scan cancellation.
- `ipw_wx_set_scan()` may leave `work == NULL` when a malformed scan request has `sizeof(struct iw_scan_req)` but neither direct nor passive conditions apply; the subsequent `schedule_delayed_work(work, 0)` would be unsafe if such a path is reachable through WEXT input.
- `ipw_wx_set_frag()` stores a normalized even `priv->ieee->fts` but sends `wrqu->frag.value` rather than the normalized stored value to firmware.
- Security handling has partial hardware crypto semantics, especially TKIP MIC and multicast decrypt. Incorrect host/hardware flag combinations can yield frames that are double-decrypted, not decrypted, or accepted contrary to policy.
- The code uses several `BUG()`/`BUG_ON()` calls for invalid channel/mode and firmware DMA assumptions. Unexpected runtime inputs can become kernel panics rather than recoverable errors.
- This chunk ends before WEXT handler tables and netdev/PCI registration, so final integration details for how these handlers are exposed must be completed from the next chunk.

## Test Signals

Useful validation signals include:

- Kernel build with combinations of `CONFIG_IPW2200_DEBUG`, `CONFIG_IPW2200_MONITOR`, `CONFIG_IPW2200_RADIOTAP`, `CONFIG_IPW2200_PROMISCUOUS`, `CONFIG_IPW2200_QOS`, and `CONFIG_PM` to cover feature-gated code and module version suffixes.
- Firmware load smoke tests for infrastructure, ad-hoc, and monitor images, checking boot firmware DMA, DINO microcode alive response, runtime firmware init interrupt, EEPROM read, queue reset, and RX replenish.
- Interrupt-path tests or hardware traces covering RX transfer, TX command completion, TX data reclaim, RF-kill done, fatal firmware error capture/restart, parity retry, and command timeout.
- WEXT behavioral tests for setting channel/frequency, mode, ESSID, BSSID, scan/direct scan/passive scan, rate masks, RTS/fragmentation/retry, TX power/RF kill, power management, WPA IE/auth/cipher/key settings, and MLME disassociation.
- Association tests across 2200BG and 2915ABG hardware, 2.4 GHz and 5 GHz geos, passive-only channels, static ESSID/BSSID/channel, ad-hoc creation/merge, open/WEP/TKIP/CCMP, and QoS-capable APs.
- RX path tests for management, data, duplicate suppression, ad-hoc station discovery, hardware-decrypted WEP/CCMP frame rebuild, monitor radiotap metadata, and optional promiscuous filter/header-only modes.
- Long-running link tests that verify missed-beacon thresholds, roam scans, disassociation thresholds, background scans, stats gathering, LED delayed work, and RF-kill toggles do not deadlock or leave stale status bits.

## Cross-Chunk Notes

The next chunk must connect this implementation to the WEXT handler arrays, private WEXT commands after `ipw_wx_get_powermode()`, netdev transmit/open/stop operations, ethtool hooks, ISR top half, link up/down work, deferred work initialization, libipw security shim, rate/geography setup, `ipw_up()`/`ipw_down()`, PCI probe/remove, PM callbacks, monitor/promiscuous netdev allocation, module parameters, and final module init/exit. It should also confirm whether the potential `ipw_wx_set_scan()` null-work path is constrained by WEXT dispatch rules or remains a reachable bug.

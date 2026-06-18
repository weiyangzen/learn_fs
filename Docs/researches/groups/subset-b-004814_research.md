# Research: subset-b-004814

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-debug.c

## Purpose

`4965-debug.c` provides the Intel 4965-specific debugfs read callbacks for firmware statistics. It does not collect counters itself; it formats the latest firmware statistics cached in `struct il_priv` into user-readable debugfs buffers. The exported integration point is `il4965_debugfs_ops`, which supplies `.rx_stats_read`, `.tx_stats_read`, and `.general_stats_read` for the iwlegacy debugfs layer.

This file is built around three firmware statistics views:

- RX PHY/non-PHY/HT counters from `il->_4965.stats.rx`.
- TX counters from `il->_4965.stats.tx`.
- General device, debug, diversity, temperature, and timestamp values from `il->_4965.stats.general.common`.

When `CONFIG_IWLEGACY_DEBUGFS` support in the wider driver tracks cumulative state, the same debugfs views also display accumulated totals, per-notification deltas, and maximum deltas from `il->_4965.accum_stats`, `il->_4965.delta_stats`, and `il->_4965.max_delta`.

## Important APIs, Types, And Functions

- `il4965_stats_flag(struct il_priv *il, char *buf, int bufsz)` decodes `il->_4965.stats.flag`, including clear-state, 2.4 GHz versus 5.2 GHz operating frequency, and TGj narrow-band status.
- `il4965_ucode_rx_stats_read()` is the debugfs file read path for RX statistics. It formats `struct stats_rx_phy` for OFDM and CCK, `struct stats_rx_non_phy` for general RX counters, and `struct stats_rx_ht_phy` for HT/OFDM aggregation counters.
- `il4965_ucode_tx_stats_read()` is the debugfs read path for `struct stats_tx`, including preamble/rx-detect, Bluetooth priority deferral/kill, timeout, ACK, collision, and aggregation scheduler counters.
- `il4965_ucode_general_stats_read()` formats `struct stats_general_common`, `struct stats_dbg`, and `struct stats_div`, including temperature, TTL timestamp, slot counters, diversity transmit/probe timing, and SOS/RX-enable counters.
- `il4965_debugfs_ops` is the externally consumed `struct il_debugfs_ops` instance used by `4965-mac.c` during PCI probe when debugfs is enabled.

The source relies on kernel helpers and driver-local structures from `common.h` and `4965.h`: `struct il_priv`, `struct il_notif_stats`, `struct stats_rx_phy`, `struct stats_rx_non_phy`, `struct stats_rx_ht_phy`, `struct stats_tx`, `struct stats_general_common`, `struct stats_dbg`, and `struct stats_div`.

## Control Flow

Each read callback follows the same pattern:

1. Read `struct il_priv *il` from `file->private_data`.
2. Refuse the operation with `-EAGAIN` if `il_is_alive(il)` is false. These files expose firmware state and require live firmware.
3. Allocate a temporary zeroed kernel buffer sized from the relevant stats structures plus formatting slack.
4. Select current, accumulated, delta, and maximum-delta views from the `_4965` substructure.
5. Append a stats flag header, a table header, and formatted rows with `scnprintf()`.
6. Return data to userspace with `simple_read_from_buffer()`, then free the temporary buffer.

The data flow is intentionally one-way: debugfs reads observe cached state and never send firmware commands, modify counters, or take ownership of the statistics. Current firmware-provided fields are little-endian and converted with `le32_to_cpu()`. Accumulated/delta/max fields are host-order `u32` values maintained elsewhere in the driver.

## State And Persistence Behavior

This file has no persistent storage of its own. Its only file-static state is the format strings `fmt_value`, `fmt_table`, and `fmt_header`. All observable state is stored in `il->_4965` and is refreshed by notification handling in `4965-mac.c`, especially `il4965_hdl_stats()` and `il4965_hdl_c_stats()`.

The debugfs output is a snapshot of the last statistics notification, not a synchronous query of the device. Comments in all three readers explicitly warn that displayed values may not reflect current firmware activity. The cumulative, delta, and max-delta columns depend on rollover-naive accumulation in the MAC file under `CONFIG_IWLEGACY_DEBUGFS`; if firmware counters wrap, the debugfs view may underreport or skip wrapped increments.

## Dependencies And Integration Points

- Depends on the firmware statistics layout and endian conventions declared in the iwlegacy headers.
- Depends on the driver liveness model through `il_is_alive()`.
- Uses memory allocation (`kzalloc`, `kfree`) and debug logging (`IL_ERR`) from the kernel/driver environment.
- Uses `simple_read_from_buffer()` to implement standard debugfs read semantics with `ppos`.
- Is attached to the rest of the driver by `il4965_debugfs_ops`; `4965-mac.c` assigns this to `il->debugfs_ops` during PCI probe under `CONFIG_IWLEGACY_DEBUGFS`, and the common debugfs registration code consumes it.

## Risks And Edge Cases

- Buffer sizing is heuristic: it multiplies structure sizes by constants and adds slack. `scnprintf()` prevents overflow, but insufficient sizing would silently truncate output.
- The read functions do not lock around the `_4965.stats` snapshot. Concurrent notification updates can produce internally mixed rows, especially between current and accumulated views.
- All current firmware stats need endian conversion; accumulated values do not. Mixing those conventions incorrectly in future edits would corrupt the printed tables.
- Allocation is per read. Very frequent debugfs polling adds allocation pressure, although this is debug-only behavior.
- If the device is not alive, users receive `-EAGAIN`; tools reading the debugfs files should tolerate transient failures during firmware load, restart, suspend, or RF-kill transitions.

## Test Signals

- With debugfs enabled and firmware alive, reading the RX, TX, and general stats files should return non-empty tables beginning with the decoded statistics flag.
- During firmware restart or interface-down states, reads should return `-EAGAIN` rather than stale-looking output.
- RX stats should include OFDM, CCK, GENERAL, and OFDM_HT sections with current/cumulative/delta/max columns.
- TX stats should include both base TX counters and `agg.*` counters.
- General stats should show temperature and TTL timestamp as single values and the rest as table rows.
- Static analysis should flag no unchecked buffer writes because all formatting uses `scnprintf()` with remaining length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-mac.c

## Purpose

`4965-mac.c` is the main Intel Wireless WiFi Link 4965 driver integration file for the Linux mac80211/PCI stack in iwlegacy. It binds the 4965 hardware to mac80211, owns PCI probe/remove, firmware discovery and loading, interrupt/tasklet dispatch, RX/TX DMA queue management, station/key/aggregation operations, scan command construction, runtime calibration scheduling, RF-kill and thermal handling, sysfs attributes, and module entry/exit.

The file is not a filesystem implementation despite the repository path containing `distributed-fs/ceph-client`; it is a Linux wireless driver source snapshot. Its behavior is centered on `struct il_priv`, the 4965-specific `_4965` state embedded in that private structure, the `il4965_ops` hardware hooks declared elsewhere, and mac80211 callbacks exposed through `il4965_mac_ops`.

## Important APIs, Types, And Functions

Driver registration and lifecycle:

- `il4965_init()` registers the iwl-4965 rate control algorithm and the PCI driver.
- `il4965_exit()` unregisters the PCI driver and rate control.
- `il4965_pci_probe()` allocates `ieee80211_hw`, maps PCI BARs, initializes EEPROM/geography/channel tables, creates IRQ/workqueue/tasklet services, sets handlers, requests firmware asynchronously, and wires debugfs/sysfs registration through the firmware callback.
- `il4965_pci_remove()` waits for firmware loading completion, unregisters debugfs/sysfs/mac80211, stops hardware, frees DMA queues, firmware buffers, EEPROM, IRQ/MSI, workqueue, and `ieee80211_hw`.
- `il4965_request_firmware()`, `il4965_load_firmware()`, and `il4965_ucode_callback()` locate API-compatible `.ucode` files, parse firmware image pieces, allocate DMA firmware descriptors, copy images, then register the mac80211 device.

mac80211 callbacks and externally visible operations:

- `il4965_mac_start()` / `il4965_mac_stop()` bring the NIC up and down for mac80211.
- `il4965_mac_tx()` submits outbound skbs to `il4965_tx_skb()`.
- `il4965_mac_set_key()` and `il4965_mac_update_tkip_key()` program or update hardware crypto.
- `il4965_mac_ampdu_action()` maps mac80211 A-MPDU start/stop actions to 4965 station and scheduler state.
- `il4965_mac_sta_add()` adds stations and initializes rate scaling.
- `il4965_mac_channel_switch()` validates and stages channel-switch commands.
- `il4965_configure_filter()` translates mac80211 filter flags to RXON filter bits.
- `il4965_mac_setup_register()` fills `struct ieee80211_hw` and `wiphy` capabilities before `ieee80211_register_hw()`.

RX path:

- `il4965_rx_init()`, `il4965_rx_queue_reset()`, `il4965_rx_queue_restock()`, `il4965_rx_replenish()`, `il4965_rx_replenish_now()`, `il4965_rx_queue_free()`, and `il4965_rxq_stop()` manage receive buffer descriptors, page allocation, DMA mapping, and RX DMA hardware registers.
- `il4965_rx_handle()` drains firmware-filled RX buffers based on the shared status write pointer, dispatches each packet to `il->handlers[pkt->hdr.cmd]`, completes reclaimable host commands, remaps or recycles pages, and restocks firmware-visible buffers.
- `il4965_hdl_rx_phy()` caches PHY data for HT MPDU notifications.
- `il4965_hdl_rx()` converts firmware RX notifications into `struct ieee80211_rx_status`, validates CRC/FIFO status, computes rate/band/frequency/RSSI/HT flags, and passes valid frames to mac80211.
- `il4965_pass_packet_to_mac80211()` handles interface-open checks, passive-channel queue wakeup, hardware decrypt status, skb allocation/page-frag transfer, stats update, and `ieee80211_rx()`.

TX path and aggregation:

- `il4965_tx_skb()` builds `C_TX` commands, selects station and queue, manages QoS sequence numbers, handles aggregation queues, maps command and payload DMA buffers, attaches TFD chunks, updates byte-count tables, advances queue pointers, and applies mac80211 queue flow control.
- `il4965_tx_cmd_build_basic()`, `il4965_tx_cmd_build_rate()`, and `il4965_tx_cmd_build_hwcrypto()` populate firmware TX command fields.
- `il4965_hw_txq_ctx_free()`, `il4965_txq_ctx_alloc()`, `il4965_txq_ctx_reset()`, `il4965_txq_ctx_stop()`, `il4965_txq_ctx_unmap()`, `il4965_hw_tx_queue_init()`, `il4965_hw_txq_attach_buf_to_tfd()`, and `il4965_hw_txq_free_tfd()` allocate, reset, stop, initialize, populate, and free TX DMA queues and TFDs.
- `il4965_tx_agg_start()`, `il4965_tx_agg_stop()`, `il4965_txq_agg_enable()`, `il4965_txq_agg_disable()`, and `il4965_txq_check_empty()` map RA/TID sessions to scheduler queues and coordinate ADDBA/DELBA state transitions with mac80211.
- `il4965_hdl_tx()` processes firmware TX responses, reclaims queue entries, updates per-TID outstanding TFD counts, reports status to mac80211, checks abort/RF-kill flush, and wakes queues.
- `il4965_hdl_compressed_ba()` and `il4965_tx_status_reply_compressed_ba()` consume block-ack notifications for aggregated frames and report A-MPDU status/rate information to mac80211.

Station, key, beacon, and scan support:

- `il4965_add_bssid_station()`, `il4965_alloc_bcast_station()`, `il4965_update_bcast_stations()`, `il4965_sta_tx_modify_enable_tid()`, `il4965_sta_rx_agg_start()`, `il4965_sta_rx_agg_stop()`, and `il4965_sta_modify_sleep_tx_count()` maintain firmware station table state.
- `il4965_set_default_wep_key()`, `il4965_remove_default_wep_key()`, `il4965_set_dynamic_key()`, `il4965_remove_dynamic_key()`, and cipher-specific helpers manage WEP/CCMP/TKIP key material.
- `il4965_request_scan()` builds firmware scan commands, including dwell times, SSID probes, per-band rates, RX/TX antenna selection, RX chain configuration, probe request payloads, and scan channel descriptors.
- `il4965_send_beacon_cmd()`, `il4965_hw_get_beacon_cmd()`, and `il4965_set_beacon_tim()` construct beacon TX commands for IBSS/beaconing flows.

Interrupts, notifications, and work:

- `il4965_setup_handlers()` maps firmware notification IDs to handlers.
- `il4965_irq_tasklet()` services acknowledged interrupt causes, including hardware/software errors, RF-kill, CT-kill, wakeup, RX, and firmware-load TX completion.
- `il4965_hdl_alive()`, `il4965_alive_start()`, and `il4965_alive_notify()` transition the device from firmware ALIVE notifications into operational scheduler, power, RXON, calibration, and queue-ready state.
- `il4965_hdl_stats()` and `il4965_hdl_c_stats()` cache statistics, maintain debugfs accumulators when enabled, trigger calibration/noise processing, and reschedule periodic stats.
- `il4965_bg_restart()`, `il4965_bg_rx_replenish()`, `il4965_bg_run_time_calib_work()`, `il4965_bg_txpower_work()`, and delayed ALIVE workers perform long-running or sleepable work outside IRQ context.

## Control Flow

Probe flow:

1. `il4965_pci_probe()` allocates mac80211 private state, assigns config/ops/debugfs ops, enables PCI, sets DMA mask, maps BAR0, resets the NIC, reads hardware revision and EEPROM, initializes hardware parameters and regulatory/geography state.
2. It disables interrupts, requests IRQ/MSI, creates the driver workqueue, initializes handlers, enables RF-kill interrupts, initializes power state, then asynchronously requests firmware.
3. `il4965_ucode_callback()` validates firmware API/size/layout, copies firmware sections into DMA buffers, sets calibration command offsets, registers mac80211/debugfs/sysfs, and completes firmware-loading synchronization. On firmware mismatch it tries lower API versions before unbinding.

Open/bring-up flow:

1. `il4965_mac_start()` calls `__il4965_up()` under `il->mutex`.
2. `__il4965_up()` allocates the broadcast station, prepares hardware, handles hardware RF-kill, initializes NIC RX/TX queues through `il4965_hw_nic_init()`, enables interrupts, restores firmware data backup, loads bootstrap/init firmware through `il->ops->load_ucode()`, starts the NIC, and waits for firmware ALIVE.
3. `il4965_hdl_alive()` receives ALIVE notifications and schedules either init or runtime ALIVE work. `il4965_alive_start()` verifies runtime firmware, initializes scheduler/DMA queue status via `il4965_alive_notify()`, sets `S_ALIVE`/`S_READY`, configures power, RXON, Bluetooth coexistence, calibrations, CT-kill, and wakes mac80211 queues.

RX flow:

1. Firmware writes frames/notifications into RX buffers and advances the shared status pointer.
2. Interrupt handling schedules/executes `il4965_irq_tasklet()`, which calls `il4965_rx_handle()` for RX interrupt bits.
3. `il4965_rx_handle()` unmaps each page, dispatches by notification command, optionally completes pending host commands, then either remaps the page into the free list or moves the buffer back to the used list.
4. Data frames pass through `il4965_hdl_rx()` and `il4965_pass_packet_to_mac80211()` into `ieee80211_rx()`.

TX flow:

1. mac80211 calls `il4965_mac_tx()`, which delegates to `il4965_tx_skb()`.
2. The driver chooses a station ID and queue, updates QoS sequence/TID bookkeeping, builds a firmware TX command, maps command/payload DMA, attaches TFD chunks, updates scheduler byte counts for A-MPDU, advances write pointers, and may stop mac80211 queues if below high-watermark space.
3. Firmware returns `C_TX`; `il4965_hdl_tx()` updates TX status, handles aggregation bookkeeping, reclaims descriptors with `il4965_tx_queue_reclaim()`, wakes queues when space returns, and reports status to mac80211.
4. Aggregated transmissions may receive `N_COMPRESSED_BA`; `il4965_hdl_compressed_ba()` aligns the BA bitmap with the scheduler sequence space, updates `IEEE80211_TX_STAT_AMPDU`, and reclaims completed TFDs.

Down/remove flow:

1. `il4965_mac_stop()` clears `is_open`, calls `il4965_down()`, flushes the workqueue, and re-enables RF-kill interrupts for userspace notifications.
2. `__il4965_down()` cancels scans, marks exit pending, stops watchdog, clears stations/keys, stops firmware/NIC, disables interrupts, synchronizes IRQ/tasklet, stops DMA queues, powers down APM, unmaps TX queues, drops beacon/free-frame state, and preserves only selected status bits.
3. PCI remove additionally unregisters mac80211/debugfs/sysfs, frees firmware/RX/TX/EEPROM resources, destroys workqueue, frees IRQ/MSI, unmaps BAR, releases PCI regions, and frees `ieee80211_hw`.

## State And Persistence Behavior

The central mutable state is `struct il_priv`. This file initializes and mutates:

- Status bits such as `S_INIT`, `S_ALIVE`, `S_READY`, `S_RFKILL`, `S_SCANNING`, `S_FW_ERROR`, `S_EXIT_PENDING`, `S_POWER_PMI`, `S_CHANNEL_SWITCH_PENDING`, and `S_STATS`.
- RX queue lists, descriptor rings, read/write indices, free counts, page DMA mappings, and `alloc_rxb_page`.
- TX queue arrays, scheduler context active mask, byte-count tables, keep-warm buffer, command queue ID, per-queue stopped counters, and per-TID `tfds_in_queue`/aggregation state.
- Firmware images in DMA descriptors: runtime code/data, data backup, init code/data, and bootstrap code.
- Station table entries, link-quality commands, WEP key cache, dynamic key counts, ucode key table bits, and broadcast/IBSS station IDs.
- Cached firmware stats and debugfs accumulators in `il->_4965`.
- Runtime calibration state, temperature, last temperature, chain-noise/sensitivity data, beacon skb, scan command buffer, and work/timer/tasklet structures.

Persistence is in-memory and device-resident only. Firmware blobs are copied from the kernel firmware loader into DMA-safe memory; station/key/RXON state is re-sent after device restart rather than persisted externally. EEPROM-derived regulatory/channel/MAC data is read during probe and freed on remove. The firmware data backup is refreshed from the original runtime data image during each `__il4965_up()` to support clean firmware starts.

Concurrency is managed with several locks:

- `il->mutex` protects sleepable high-level configuration, start/stop, key, scan, and mac80211 control paths.
- `il->lock` protects device queue/register operations and many interrupt-sensitive paths.
- `il->sta_lock` protects station table, TID, aggregation, and key state.
- `il->reg_lock` protects low-level NIC register access sequences.
- RX queue has its own `rxq->lock`.

Timers and workqueues persist across the device lifetime from probe to remove. Work is cancelled during down/remove to prevent use-after-free against firmware, queues, or mac80211 state.

## Dependencies And Integration Points

Kernel subsystems:

- PCI core for device matching, BAR mapping, DMA masks, MSI/IRQ, config space, and driver registration.
- mac80211/cfg80211 for `ieee80211_hw`, TX/RX callbacks, station/key/AMPDU operations, scanning, channel switching, regulatory capability exposure, and TX/RX status reporting.
- Firmware loader via `request_firmware_nowait()` and `release_firmware()`.
- DMA mapping API for coherent queue/firmware buffers and streaming skb/page mappings.
- Workqueue, timer, tasklet, waitqueue, completion, spinlock, mutex, skb, page allocation, sysfs, debugfs, rfkill, and LED helpers.

Driver-local integration:

- `common.h` supplies common iwlegacy infrastructure such as command submission, RXON helpers, station helpers, scan helpers, EEPROM/regulatory helpers, queue helpers, rate tables, debug macros, watchdog, interrupt top half, and power helpers.
- `4965.h` supplies 4965-specific constants, structures, firmware command layouts, stats layouts, scheduler/register definitions, and `il4965_ops`/`il4965_cfg` declarations.
- `4965-debug.c` contributes `il4965_debugfs_ops`, assigned during probe when debugfs is enabled.
- Hardware-specific operations are invoked through `il->ops`, including firmware loading, TX power, RX chain setup, channel switch, TFD operations, and RTC address validation.

## Risks And Edge Cases

- The driver contains several interrupt/DMA race-sensitive paths. RX pages can be consumed by handlers and set to `NULL`, so code after handler dispatch must check `rxb->page` before touching packet memory.
- TX DMA mapping error paths in `il4965_tx_skb()` jump to a common drop path; future edits must avoid leaking a successfully mapped first or second buffer when a later mapping fails.
- Aggregation state transitions depend on per-TID `tfds_in_queue`, scheduler SSN values, and queue read/write pointers. Incorrect locking or queue ID reuse can desynchronize mac80211 ADDBA/DELBA callbacks from firmware state.
- `il4965_accumulative_stats()` is explicitly rollover-naive. Debugfs cumulative stats are diagnostic, not precise long-term counters.
- Firmware loading retries lower API versions; errors before and after DMA allocation have different cleanup behavior. Changes in callback error paths can cause unbind races or leaked firmware descriptors.
- RF-kill and CT-kill paths intentionally allow partial bring-up or command blocking. Code that assumes `mac_start()` always reaches `S_READY` can mishandle hardware-kill states.
- Many paths call into firmware synchronously while holding `il->mutex`; call sites must avoid being invoked from atomic context unless specifically using asynchronous variants.
- Some WARN/BUG_ON checks protect queue invariants. A malformed queue state can escalate from a logged error to a kernel BUG in RX restock paths.
- Hardware crypto handling has cipher-specific semantics: TKIP receives phase1 key updates separately, WEP has default and dynamic modes, and IBSS group keys are intentionally left to software for RSN.

## Test Signals

Useful validation signals include:

- Module load registers the `iwl4965` PCI driver and rate control algorithm; module unload unregisters both without leaked workqueue/IRQ/DMA resources.
- Probe logs hardware revision, EEPROM-derived MAC, firmware version, and creates sysfs `temperature`/`tx_power` attributes plus debugfs hooks when configured.
- `mac_start()` reaches `S_READY` after runtime ALIVE within `UCODE_READY_TIMEOUT`; RF-kill start returns without hard failure but exposes rfkill state.
- RX traffic increments handler stats and reaches mac80211 with plausible band/frequency/rate/signal fields; malformed CRC/FIFO frames are dropped.
- TX traffic produces `C_TX` responses, descriptor reclamation, mac80211 TX status, queue wake/stop behavior around watermarks, and no lingering skbs in TX queues after stop.
- A-MPDU start/stop exercises scheduler queue activation above `IL49_FIRST_AMPDU_QUEUE`, compressed BA handling, and mac80211 BA callbacks.
- Scan requests produce nonzero channel counts, respect passive/no-IR channels, and clear `S_SCAN_HW` on command failure.
- Key tests should cover CCMP, TKIP, dynamic WEP, default WEP, software-crypto fallback, RF-kill key removal, and IBSS group-key software fallback.
- Firmware error, hardware error, RF-kill toggle, and CT-kill injection should schedule restart/down paths without use-after-free or dead work items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-mac.c -->

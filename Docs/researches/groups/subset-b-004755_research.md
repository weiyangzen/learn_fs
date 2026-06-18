# subset-b-004755 ath5k core research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ath5k.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ath5k.h

## Purpose
`ath5k.h` is the central private interface for the ath5k driver. It defines chip IDs, register access helpers, timing constants, hardware revision enums, public driver state, descriptor callback slots, and prototypes shared by the ath5k hardware, PHY, DMA, interrupt, beacon, EEPROM, GPIO, ANI, and mac80211 integration code.

## Important APIs, types, and constants
- Logging and register helpers: `ATH5K_PRINTK`, `ATH5K_INFO/WARN/ERR`, `AR5K_REG_SM`, `AR5K_REG_MS`, `AR5K_REG_WRITE_BITS`, `AR5K_REG_ENABLE_BITS`, `AR5K_REG_DISABLE_BITS`, queue bit helpers, and inline `ath5k_hw_reg_read/write`.
- Hardware identity: PCI device IDs, `enum ath5k_version`, `enum ath5k_radio`, silicon revision defines for MAC, PHY, and radio.
- PHY and timing model: bandwidth modes, antenna modes, slot/SIFS/latency constants, beacon timer constants, power modes, calibration masks, and rate-code mappings.
- TX/RX model: `struct ath5k_tx_status`, `struct ath5k_rx_status`, `struct ath5k_txq`, `struct ath5k_txq_info`, queue type/subtype/id enums, packet type enum, and TX/RX error flags.
- Device state: `struct ath5k_hw` embeds `ath_common`, mac80211 state, channel/rate tables, DMA descriptor storage, RX/TX/beacon lists, locks, tasklets/work items, interrupt masks, rfkill/LED state, capabilities, EEPROM-derived data, calibration timers, ANI state, txpower state, function pointers for descriptors, and bus operations.
- Bus abstraction: `struct ath_bus_ops` supplies cache-size reading, EEPROM reads, and MAC-address reads for PCI/AHB wrappers.

## Control flow and integration
This header is included by most ath5k implementation files and forms the contract between the mac80211-facing code in `base.c`, the low-level hardware helpers in files such as `reset.c`, `dma.c`, `pcu.c`, `phy.c`, `qcu.c`, `desc.c`, and the EEPROM/capability paths. The descriptor callbacks in `ath5k_hw` are assigned during attach and let higher-level TX/RX code call one interface while `desc.c` selects AR5210/5211 2-word or AR5212 4-word descriptor handling. Inline register access switches between normal MMIO and AHB special register routing under `CONFIG_ATH5K_AHB`.

## State and persistence behavior
Most state is runtime kernel memory: descriptor DMA memory, SKB mappings, queue lists, counters, calibration timestamps, ANI variables, txpower tables, current channel/opmode, and EEPROM-derived capability data. Persistent hardware identity and calibration inputs come from EEPROM through `ath5k_hw_nvram_read`; this header stores those values in `ah_capabilities.cap_eeprom` and exposes them to other subsystems. No filesystem persistence is defined here.

## Dependencies
The file depends on Linux kernel MMIO, interrupt, LED, average, cfg80211, and mac80211 headers, plus local ath5k headers `desc.h`, `eeprom.h`, `debug.h`, `ani.h`, and shared ath headers `../ath.h`. Many constants assume register definitions from `reg.h`, although that header is included by implementation files rather than here.

## Risks and edge cases
- Register macros perform read-modify-write operations directly against device MMIO; callers need correct locking and reset/invalid-state discipline.
- The header centralizes many hardware-generation differences. Incorrect `ah_version`, `ah_radio`, or revision classification cascades into queue count, descriptor layout, PHY setup, crypto features, and rate handling.
- `ath5k_hw_hasbssidmask` and `ath5k_hw_hasveol` macros ignore their argument name and reference `ah`, which is fragile if used outside scopes with that variable.
- Fixed descriptor/buffer counts and channel-table sizing make bounds handling important when adding modes or channels.
- AHB register routing for AR2315/AR2317 relies on revision ranges and special physical mappings.

## Test signals
Useful evidence includes successful module probe logs with MAC/PHY/radio names, correct mac80211 band/channel registration, stable TX/RX under reset and channel-switch paths, debugfs register/queue/ANI output, no WARNs from invalid rates or descriptor setup, and correct EEPROM capability interpretation across AR5210, AR5211, AR5212, PCI, and AHB devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ath5k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/attach.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/attach.c

## Purpose
`attach.c` performs early hardware attach for an ath5k device. It identifies the MAC/radio generation, validates support, performs a register POST, initializes EEPROM and capability data, configures selected PCIe power-save registers, initializes common addressing/opmode state, and tears down hardware-private attach resources on detach.

## Important APIs and functions
- `ath5k_hw_post(struct ath5k_hw *ah)`: writes variable and static test patterns to `AR5K_STA_ID0` and `AR5K_PHY(8)`, verifies readback, and restores original values.
- `ath5k_hw_init(struct ath5k_hw *ah)`: top-level hardware init used from `ath5k_init_ah`.
- `ath5k_hw_deinit(struct ath5k_hw *ah)`: marks the device invalid, frees RF banks, and detaches EEPROM state.

## Control flow
`ath5k_hw_init` seeds defaults such as bandwidth, retry limits, antenna mode, ANI mode, noise floor, and current channel. It reads the silicon revision with `ath5k_hw_read_srev`, classifies `ah_version` and `ah_mac_version`, then initializes descriptor function pointers via `ath5k_hw_init_desc_functions`. It wakes and resets the NIC with `ath5k_hw_nic_wakeup`, reads PHY/radio revisions, and maps the radio to RF5110/RF5111/RF5112/RF2413/RF5413/RF2316/RF2317/RF2425 using radio, MAC, and PHY revision fallbacks.

Unsupported chips in the AR5416-to-before-AR2425 range are rejected. The POST runs after support filtering. Newer Hainan and later chips receive the PCI retry fix. EEPROM initialization follows, then AR5212 PCIe devices get a sequence of SERDES writes, influenced by `ee_serdes`, and a SERDES reset. Capabilities are computed by `ath5k_hw_set_capabilities`; crypto limits are filled into `ath_common`; AES-CCM and combined MIC support are enabled based on revision and EEPROM bits. The function clears the MAC address until interface creation, sets broadcast BSSID, applies opmode, initializes RF gain and noise-floor history, and turns on hardware LEDs.

## State and persistence behavior
The function writes persistent-in-session state into `struct ath5k_hw` and `struct ath_common`: version/radio fields, capability flags, crypto capabilities, EEPROM info, RF gain/noise calibration state, initial opmode/BSSID, and LED state. It reads persistent EEPROM contents but does not write them. Hardware registers are modified during wakeup, POST, PCIe SERDES setup, retry-fix enablement, opmode/BSSID setup, and LED initialization.

## Dependencies and integration points
This file depends on PCI helpers, `reg.h`, EEPROM code, descriptor setup in `desc.c`, capability logic in `caps.c`, PHY helpers for radio revision/RF gain/noise history, PCU address/opmode helpers, LED helpers, and shared ath crypto state. It is called from the broader mac80211 attach path in `base.c` after IRQ/common bus state is prepared but before the hardware is registered with mac80211.

## Risks and edge cases
- POST writes to live registers and returns immediately on mismatch without restoring the current register in that failing iteration, so callers depend on later reset/error unwind.
- Radio identification is revision-sensitive and contains several fallback heuristics; misclassification can select wrong PHY/radio programming.
- PCIe SERDES writes are magic constants and must stay limited to AR5212 PCIe devices.
- Unsupported-chip filtering excludes AR5416/AR5418-era devices while allowing AR2425 and later matching code paths.
- `ath5k_hw_deinit` assumes interrupts are already down; callers must order detach correctly.

## Test signals
Probe should log expected AR and RF names, reject unsupported silicon with `-ENODEV`, initialize EEPROM without error, expose correct crypto capabilities, preserve stable register access after POST, and cleanly unload without leaks or IRQ activity after `ath5k_hw_deinit`. PCIe devices should resume from link power states without SERDES-related failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/base.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/base.c

## Purpose
`base.c` is the main mac80211-facing ath5k driver implementation. It registers hardware capabilities, builds channel/rate tables, allocates DMA descriptors and software buffers, manages RX/TX queues, handles interrupts and tasklets, performs reset/start/stop/deinit, configures beaconing, exposes regulatory integration, and converts hardware descriptor status into mac80211 RX/TX status.

## Important APIs, functions, and data
- Module parameters: `nohwcrypt`, `fastchanswitch`, and `no_hw_rfkill_switch`.
- Static data: `srev_names` for chip naming and `ath5k_rates` for CCK/OFDM rate mappings.
- mac80211 lifecycle: `ath5k_init_ah`, `ath5k_deinit_ah`, `ath5k_start`, `ath5k_stop`, internal `ath5k_init`, `ath5k_reset`, `ath5k_stop_locked`, and `ath5k_reset_work`.
- Channel/rate setup: `ath5k_setup_channels`, `ath5k_setup_bands`, `ath5k_setup_rate_idx`, `ath5k_chan_set`.
- Interface state: `ath5k_vif_iter`, `ath5k_update_bssid_mask_and_opmode`, `ath5k_any_vif_assoc`, `ath5k_set_beacon_filter`.
- DMA and buffers: `ath5k_desc_alloc/free`, `ath5k_rx_skb_alloc`, `ath5k_rxbuf_setup`, `ath5k_txbuf_setup`, `ath5k_txbuf_free_skb`, `ath5k_rxbuf_free_skb`.
- RX/TX processing: `ath5k_tasklet_rx`, `ath5k_receive_frame_ok`, `ath5k_receive_frame`, `ath5k_tx_queue`, `ath5k_tx_processq`, `ath5k_tasklet_tx`, `ath5k_tx_frame_completed`.
- Beaconing: `ath5k_beacon_setup`, `ath5k_beacon_update`, `ath5k_beacon_send`, `ath5k_beacon_update_timers`, `ath5k_beacon_config`, `ath5k_tasklet_beacon`.
- Interrupt/calibration: `ath5k_intr`, `ath5k_intr_calibration_poll`, `ath5k_calibrate_work`, `ath5k_tasklet_ani`, `ath5k_tx_complete_poll_work`.

## Control flow
Attach starts in `ath5k_init_ah`: it sets mac80211 feature flags, supported interface combinations, antenna masks, IRQ handler, bus/common operations, cache line size, calls `ath5k_hw_init`, configures MRR limits, then calls internal `ath5k_init`. `ath5k_init` builds supported bands from capability bits and regulatory-compatible channel checks, allocates descriptor DMA memory and buffer objects, sets up beacon/CAB/data queues, initializes tasklets/work items, reads the permanent MAC from EEPROM, initializes regulatory state, registers the hw with mac80211, then initializes LEDs and sysfs.

Runtime start is `ath5k_start`: stop any old state, set the current channel and interrupt mask, call `ath5k_reset`, start hardware rfkill if enabled, clear key cache, reset beacon slots, mark started, and queue TX completion polling. `ath5k_reset` disables interrupts, kills tasklets, disables ANI, drains TX, stops RX PCU/DMA, optionally fast-switches channel, calls `ath5k_hw_reset`, rebuilds RX descriptors, restores ANI, schedules calibration deadlines, clears survey/cycle counters, configures beacons and wakes mac80211 queues.

TX flow starts at `ath5k_tx_queue`: add 4-byte MAC header padding if needed, stop queues on high-water marks or no buffers, pull a free `ath5k_buf`, and call `ath5k_txbuf_setup`. That maps the skb for DMA, merges station rate tables or asks mac80211 for rates, resolves key index, RTS/CTS/CTS-to-self settings, fills the version-specific descriptor through `ah_setup_tx_desc`, optionally fills MRR, links the descriptor to the hardware queue, and starts TX DMA. Completion arrives through interrupts into `ath5k_tasklet_tx`, which processes queues selected by ISR bits, converts status into `ieee80211_tx_status_skb`, unmaps DMA, and recycles buffers while avoiding a hardware race on the last descriptor.

RX flow is descriptor-ring based. `ath5k_rx_start` creates a self-linked tail ring and starts RX DMA/PCU. `ath5k_tasklet_rx` walks descriptors until the hardware-owned descriptor or in-progress status, filters acceptable frames, replaces the SKB before handing the old one up, unmaps DMA, sets `ieee80211_rx_status`, extends timestamps, tracks beacon RSSI/IBSS TSF, and calls `ieee80211_rx`.

Interrupt flow loops over ISR status until no PCI interrupt remains or a safety counter expires. Fatal and older RX overrun conditions schedule reset work. RX/TX statuses schedule tasklets, SWBA schedules beacon work, TX underrun raises trigger level, MIB updates counters and ANI, and GPIO schedules rfkill. RX/TX interrupts are temporarily masked while tasklets are pending.

## State and persistence behavior
All runtime state lives in `ath5k_hw`, `ath_common`, DMA-coherent descriptor memory, SKBs, work/tasklet state, and hardware registers. The file tracks queue lengths, buffer pools, BSSID masks, current opmode/channel, beacons, calibration deadlines, survey counters, and error statistics. It reads EEPROM MAC/regdomain through bus ops. No persistent file state is written. Hardware state persists only until reset, stop, suspend, or module unload.

## Dependencies and integration points
The file depends heavily on mac80211/cfg80211 APIs, Linux DMA mapping, IRQ/tasklet/workqueue primitives, list/spinlock/mutex primitives, shared ath helpers for crypto/regulatory/cycle counters, ath5k hardware helpers from `ath5k.h`, register definitions, ANI, descriptor functions, LED/sysfs/rfkill helpers, and tracepoints. It bridges bus-specific probe code with mac80211 registration and the lower hardware files.

## Risks and edge cases
- DMA and descriptor ownership are race-prone; the code intentionally keeps the last TX descriptor and uses self-linked RX descriptors to avoid hardware races.
- Reset ordering is critical: interrupts/tasklets, ANI, TX drain, PCU/DMA stop, hardware reset, RX restart, beacon config, and queue wake must remain synchronized under `ah->lock`.
- `ath5k_start` sets `ATH_STAT_STARTED` and schedules polling after `done` even if reset returned an error, which is worth scrutiny when changing start error handling.
- Header padding mutates SKBs before DMA and must be removed on TX completion/RX receive paths.
- `ath5k_extend_tsf` depends on timely RX processing of 15-bit timestamps.
- Multi-vif BSSID mask and opmode logic has special promiscuous behavior for multiple STA interfaces and limited mixed-mode assumptions.

## Test signals
Important signals include successful `ieee80211_register_hw`, visible 2 GHz/5 GHz bands and rate maps, stable `ip link set up/down`, scanning and channel switching, AP/IBSS beacon generation, TX status ACK/retry reporting, RX FCS/decrypt/MIC behavior, rfkill GPIO toggles, debugfs queue/frameerror counters, no stuck TX queue resets during normal load, no interrupt storms, and clean module unload after active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/base.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/base.h

## Purpose
`base.h` is the public local header for the mac80211-facing ath5k base layer. It declares lightweight structures used by `base.c` and other ath5k files, plus lifecycle, beacon, channel, buffer, TX queue, and chip-name entry points.

## Important APIs and types
- `enum ath5k_srev_type` and `struct ath5k_srev_name`: classify and name MAC/radio silicon revisions.
- `struct ath5k_buf`: software wrapper for one DMA descriptor, descriptor bus address, optional SKB, SKB DMA address, and up to four rate stages.
- `struct ath5k_vif`: per-vif driver private state, association state, opmode, beacon slot, and beacon buffer.
- `struct ath5k_vif_iter_data`: aggregation state used while iterating active mac80211 interfaces to compute BSSID masks, active MAC, opmode, and association presence.
- Prototypes for start/stop, beacon update/config/filtering, BSSID/opmode updates, channel set, buffer free helpers, TX enqueue, chip name, attach, and detach.
- Hardware feature macros `ath5k_hw_hasbssidmask` and `ath5k_hw_hasveol`.

## Control flow and integration
mac80211 callbacks and bus probe/remove paths use the functions declared here. `ath5k_init_ah` and `ath5k_deinit_ah` are the high-level attach/detach API used after bus code has allocated `ieee80211_hw` and mapped device resources. `ath5k_start` and `ath5k_stop` are hardware lifecycle callbacks. Beacon functions are used by interface configuration and software beacon alerts. `ath5k_tx_queue` is the local bridge from mac80211 TX to a selected ath5k hardware queue.

## State and persistence behavior
The structures declared here describe runtime-only state. `ath5k_buf` entries persist for the lifetime of the device allocation and are recycled between free lists and active queues. `ath5k_vif` persists for the lifetime of a mac80211 virtual interface. No persistent storage is created; hardware capabilities and EEPROM-derived settings are stored in the larger `ath5k_hw` defined in `ath5k.h`.

## Dependencies
This header forward-declares kernel/mac80211 and ath5k structures to avoid heavy includes. It depends conceptually on Linux list/DMA/SKB/mac80211 types through included users, and it is paired with `base.c`, `ath5k.h`, and the bus-specific probe files.

## Risks and edge cases
- `ath5k_buf` couples software list ownership, DMA mapping, descriptor ownership, and SKB lifetime. Callers must use the correct free helper for TX vs RX mappings.
- `ath5k_vif_iter_data` fields are filled across atomic interface iteration, so users must initialize every field before iteration.
- The `ath5k_hw_hasbssidmask` and `ath5k_hw_hasveol` macros use `ah` instead of their `_ah` parameter, which can compile only in scopes where `ah` exists and can surprise future callers.
- Queue mapping assumes the order chosen in `base.c` matches mac80211 queue numbering.

## Test signals
Compile coverage catches prototype drift. Runtime signals include correct interface add/remove behavior, accurate BSSID masks for multiple vifs, beacon slot assignment, safe buffer recycling, and no DMA unmap warnings during stop/reset/deinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/caps.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/caps.c

## Purpose
`caps.c` translates hardware generation and EEPROM header data into ath5k capability flags. It determines supported bands/modes, raw frequency ranges, TX queue count, PHY error counter availability, and multi-rate retry support. It also exposes legacy AR5210 PS-Poll enable/disable helpers.

## Important APIs and functions
- `ath5k_hw_set_capabilities(struct ath5k_hw *ah)`: fills `ah->ah_capabilities`.
- `ath5k_hw_enable_pspoll(struct ath5k_hw *ah, u8 *bssid, u16 assoc_id)`: clears AR5210 PS-Poll disable/default antenna bits.
- `ath5k_hw_disable_pspoll(struct ath5k_hw *ah)`: sets the same AR5210 bits to disable PS-Poll.

## Control flow
`ath5k_hw_set_capabilities` reads `caps->cap_eeprom.ee_header`. AR5210 is hard-coded to middle 5 GHz only and 802.11a mode. Later chips use EEPROM mode bits: 11a enables 5 GHz, optionally lowering the minimum to 4920 MHz when the regulatory helper allows 4.9 GHz; 11b and 11g enable 2 GHz ranges and modes unless `cap_needs_2GHz_ovr` requests SoC-specific override. RF2112 clears 11a because that 2 GHz radio cannot support it. Queue count is two for AR5210 without QCU and ten for later devices. PHY error counters are present from AR5213A. Multi-rate retry is flagged for AR5212.

## State and persistence behavior
The file mutates only in-memory capability fields and, for PS-Poll helpers, the `AR5K_STA_ID1` hardware register. It consumes EEPROM-derived values that were populated earlier by EEPROM initialization, but it does not read or write EEPROM directly.

## Dependencies and integration points
Capabilities feed `base.c` band setup, queue setup, MRR configuration, debugfs ANI reporting, and crypto/mac80211 feature decisions made around attach. The file depends on `ath5k.h`, `reg.h`, debug logging, and shared regulatory helper `ath_is_49ghz_allowed`.

## Risks and edge cases
- EEPROM header interpretation is the source of truth for advertised bands. Bad EEPROM reads can hide supported bands or expose invalid ones.
- `cap_needs_2GHz_ovr` is externally set for SoCs; if not set correctly, 2 GHz mode bits may be wrong.
- Raw range limits are broader than final regulatory permissions; callers must still apply cfg80211/regulatory filtering.
- PS-Poll helpers only support AR5210 and return `-EIO` for later chips, so generic callers must handle non-support.

## Test signals
Probe on representative AR5210, AR5211, AR5212, RF2112, RF2413/RF5413, and AHB SoC devices should show expected band exposure, queue count, MRR max-rates behavior, PHY error counter debugfs reporting, and no illegal 5 GHz mode on RF2112. Regulatory tests should verify that 4.9 GHz exposure depends on regdomain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/caps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/debug.c

## Purpose
`debug.c` implements optional ath5k debugfs support and descriptor/band dump helpers. It exposes live register snapshots, beacon timers, debug-level toggles, antenna state, RX filter/opmode state, frame error counters, ANI state and controls, queue state/control, raw EEPROM contents, and descriptor dumps when `CONFIG_ATH5K_DEBUG` is enabled.

## Important APIs and functions
- Module parameter `debug` seeds `ah->debug.level`.
- `ath5k_debug_init_device(struct ath5k_hw *ah)`: creates `ath5k` debugfs files under the wiphy debugfs directory.
- File operations: `debug`, `registers`, `beacon`, `reset`, `antenna`, `misc`, `eeprom`, `frameerrors`, `ani`, `queue`, and bool `32khz_clock`.
- Dump helpers used by other files: `ath5k_debug_dump_bands`, `ath5k_debug_printrxbuffs`, `ath5k_debug_printtxbuf`.

## Control flow
Debugfs readers format state into bounded stack buffers and return data via `simple_read_from_buffer`, except `registers` uses seq_file iteration and `eeprom` allocates a vmalloc buffer at open. Writers parse short text commands copied from user memory. `debug` toggles named debug bits. `beacon` directly enables/disables beacon register bits. `reset` queues reset work. `antenna` switches antenna mode or clears antenna counters. `frameerrors` clears RX/TX error counters. `ani` changes ANI mode and individual immunity/weak-signal controls. `queue` wakes or stops mac80211 queues.

## State and persistence behavior
The file reads and mutates live driver and hardware state only. It can change hardware registers, queue state, antenna mode, ANI behavior, and software counters while the device is running. The EEPROM file reads NVRAM contents into a temporary buffer and frees it on release. Debug level is initialized from the module parameter and then can be changed at runtime through debugfs; it is not persisted across module unload.

## Dependencies and integration points
This file depends on debugfs, seq_file, user-copy helpers, vmalloc/kmalloc, register definitions, base-layer types, ANI functions, EEPROM/NVRAM bus ops, and descriptor callbacks. It is initialized from `ath5k_init_ah` after successful hardware setup. Its print helpers are called from `base.c` during RX stop and TX drain.

## Risks and edge cases
- Debugfs write commands can alter live hardware behavior, including reset, queue stop/start, beacon enable, antenna mode, and ANI settings.
- Most read buffers are fixed-size and truncate output if state grows; this is acceptable but may hide some detail.
- `open_file_eeprom` bounds EEPROM size to 4096 words, but still reads every word synchronously and can fail midway.
- Register reads assume the device remains valid; debugfs lifetime is tied to wiphy cleanup, so ordering must avoid access after invalidation.
- Descriptor dump helpers call descriptor processing callbacks while holding locks and are gated by debug level.

## Test signals
With `CONFIG_ATH5K_DEBUG`, debugfs should contain all expected files under the phy directory. Reads should complete without warnings while the interface is up and down. Writes such as `reset`, `frameerrors` clear, `ani-on/off`, and queue start/stop should produce expected behavior. Descriptor/band dumps should appear only when matching debug bits are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/debug.h

## Purpose
`debug.h` defines the ath5k debug-level bitmask, the per-device debug state, and the conditional debug logging/dump API. It provides no-op inline replacements when debug support is disabled.

## Important APIs and types
- `struct ath5k_dbg_info`: stores the active debug bitmask.
- `enum ath5k_debug_level`: bits for reset, interrupt, mode, transmit, beacon, calibration, txpower, LED, band dumps, DMA, ANI, descriptor dumps, and all-level output.
- `ATH5K_DBG` and `ATH5K_DBG_UNLIMIT`: conditional debug print macros. The first is net-ratelimited, the second is not.
- Functions declared under `CONFIG_ATH5K_DEBUG`: `ath5k_debug_init_device`, `ath5k_debug_printrxbuffs`, `ath5k_debug_dump_bands`, and `ath5k_debug_printtxbuf`.
- Disabled-debug inline stubs keep callers compiled without runtime work.

## Control flow and integration
Implementation files call `ATH5K_DBG` at reset, interrupt, TX, beacon, calibration, DMA, ANI, and descriptor points. When enabled, the macros check `ah->debug.level` and call `ATH5K_PRINTK`; when disabled, the compiler sees empty inline functions. `ath5k_debug_init_device` is invoked after attach, while dump helpers are invoked from band setup, RX stop, and TX drain paths.

## State and persistence behavior
Only a per-device runtime bitmask is modeled here. The initial value comes from the `debug` module parameter in `debug.c`, and debugfs writes may toggle it. There is no persistent state.

## Dependencies
The header forward declares ath5k and SKB structures and depends on `ATH5K_PRINTK` from `ath5k.h` when debug is enabled. In the disabled path it includes `linux/compiler.h` for printf attributes.

## Risks and edge cases
- `ATH5K_DBG_UNLIMIT` can produce high log volume if enabled in hot paths such as beacon handling.
- Debug logging references `ah->debug.level`; callers must pass a valid `struct ath5k_hw *`.
- The no-op implementation changes observability substantially between debug and non-debug builds, so tests that rely on debugfs/log output must account for config.

## Test signals
Build both with and without `CONFIG_ATH5K_DEBUG`. In debug builds, enabling individual levels via debugfs should emit matching logs and dumps. In non-debug builds, callers should compile cleanly and produce no debugfs-dependent symbols or output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/desc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/desc.c

## Purpose
`desc.c` implements version-specific hardware descriptor setup and status parsing for ath5k DMA. It hides AR5210/AR5211 2-word TX descriptors and AR5212 4-word TX descriptors behind callback pointers in `struct ath5k_hw`, and provides common RX descriptor setup/status parsing.

## Important APIs and functions
- TX setup: `ath5k_hw_setup_2word_tx_desc`, `ath5k_hw_setup_4word_tx_desc`.
- MRR setup: `ath5k_hw_setup_mrr_tx_desc`.
- TX status parse: `ath5k_hw_proc_2word_tx_status`, `ath5k_hw_proc_4word_tx_status`.
- RX setup: `ath5k_hw_setup_rx_desc`.
- RX status parse: `ath5k_hw_proc_5210_rx_status`, `ath5k_hw_proc_5212_rx_status`.
- Attach hook: `ath5k_hw_init_desc_functions`.

## Control flow
Attach calls `ath5k_hw_init_desc_functions` after identifying the MAC generation. That assigns `ah_setup_tx_desc`, `ah_proc_tx_desc`, and `ah_proc_rx_desc`. TX enqueue in `base.c` calls the selected setup function after DMA mapping an skb. The setup functions validate nonzero retry count and nonzero rate to avoid dangerous hardware behavior, compute frame length excluding software padding and including FCS, round beacon buffer length, fill encryption key fields when present, encode frame type, antenna, no-ack, interrupt, VEOL, RTS/CTS, CTS-to-self, rate, retry, and txpower fields. AR5212 setup additionally writes four control words and supports CTSENA/MRR.

TX completion paths call the selected status parser. The parser checks the DONE bit, returns `-EINPROGRESS` if hardware still owns the descriptor, and fills `ath5k_tx_status` with timestamp, retry counts, sequence, ACK RSSI, antenna, final MRR index, and error flags for excessive retry, FIFO underrun, and filtered frames.

RX setup clears descriptor state and writes buffer length plus optional interrupt request. RX parsers check DONE, extract length, RSSI, rate, antenna, timestamp, key index, more-fragment flag, and map hardware error bits into `AR5K_RXERR_*`. AR5212 PHY errors optionally feed ANI when hardware PHY error counters are unavailable.

## State and persistence behavior
The file writes DMA descriptors in coherent memory shared with hardware and reads status words written by hardware. It does not allocate memory or persist state itself. `READ_ONCE` is used for AR5212 status words to avoid compiler reordering or duplicate loads from hardware-updated memory.

## Dependencies and integration points
It depends on descriptor layout definitions in `desc.h`, register bit helpers in `ath5k.h`, hardware version fields, ANI error reporting, and debug logging. It is used directly by `base.c` TX/RX paths through function pointers.

## Risks and edge cases
- Zero rate with nonzero retries can cause continuous noise transmission; the code explicitly warns and rejects this.
- Frame/buffer length field overflows return `-EINVAL`; callers must handle descriptor setup failure and unmap DMA.
- AR5210/AR5211 timestamp width comments note uncertainty around 13-bit versus 15-bit assumptions.
- Descriptor memory is hardware-shared, so status readiness and field ordering are race-sensitive.
- MRR only applies to AR5212; older devices silently ignore it.

## Test signals
Exercise TX with ACKed frames, excessive retries, FIFO underruns, filtered frames, RTS/CTS, no-ack, hardware encryption, beacons, and MRR rates. Exercise RX with CRC, PHY, decrypt, MIC, key-index, and restart PHY errors. Look for no WARNs on zero rates, no DMA leaks after setup failures, correct mac80211 status reporting, and valid debug descriptor dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/desc.h

## Purpose
`desc.h` defines the packed hardware DMA descriptor layouts and bit fields used by ath5k TX/RX descriptor setup and status parsing. It documents the differences between AR5210/AR5211 2-word TX descriptors, AR5212 4-word TX descriptors, and common RX descriptors.

## Important APIs, types, and constants
- RX descriptor structs: `struct ath5k_hw_rx_ctl`, `struct ath5k_hw_rx_status`, `struct ath5k_hw_all_rx_desc`.
- TX descriptor structs: `struct ath5k_hw_2w_tx_ctl`, `struct ath5k_hw_4w_tx_ctl`, `struct ath5k_hw_tx_status`, `struct ath5k_hw_5210_tx_desc`, `struct ath5k_hw_5212_tx_desc`.
- Unified descriptor: `struct ath5k_desc` with `ds_link`, `ds_data`, and a union for TX/RX hardware-specific payload.
- Bit definitions for RX length/status/rate/RSSI/antenna/timestamp/key/PHY/MIC errors across 5210/5211 and 5212.
- Bit definitions for TX frame length, buffer length, key index, frame type, antenna, interrupt, RTS/CTS, no-ack, VEOL, txpower, retries, rates, final status, retry counters, sequence, ACK RSSI, and antenna.
- Public descriptor flags: `AR5K_RXDESC_INTREQ`, `AR5K_TXDESC_CLRDMASK`, `NOACK`, `RTSENA`, `CTSENA`, `INTREQ`, and `VEOL`.

## Control flow and integration
`desc.c` uses these definitions to encode control words before handing descriptors to hardware and to decode completion status after hardware DMA. `base.c` allocates arrays of `struct ath5k_desc`, links them into RX/TX/beacon rings through `ds_link`, and stores data-buffer physical addresses in `ds_data`. The hardware reads control fields for transmit/receive operations and writes status fields on completion.

## State and persistence behavior
The structures in this file describe DMA-coherent runtime memory. Hardware and driver share ownership of descriptor fields, so the exact packed layout and 4-byte alignment are part of the hardware ABI. There is no persistent storage; descriptor contents are recreated during allocation, reset, RX refill, TX enqueue, and beacon setup.

## Dependencies
This header relies on fixed-width integer types and kernel packing/alignment attributes supplied by includers. Semantic use depends on `ath5k.h` register helper macros, `desc.c`, and hardware generation state.

## Risks and edge cases
- Any layout, packing, alignment, or bit-mask change can break hardware DMA.
- Several fields differ by MAC generation, including antenna encoding, key index width, frame type location, timestamp width, and error bits.
- Some comments indicate historical ambiguity, such as retry count naming and AR5210 timestamp interpretation.
- PHY error code bits overlay key-index fields on AR5212, so parsers must branch on error state before interpreting key metadata.
- Endianness and DMA coherency assumptions must match the platform and descriptor initialization paths.

## Test signals
Descriptor tests are mostly integration-level: successful RX/TX DMA on AR5210, AR5211, and AR5212 hardware; correct RSSI/rate/key/error status in mac80211; no corrupted descriptor dumps; stable operation on big-endian builds; no queue hangs after beacons or MRR traffic; and no invalid memory accesses under high RX/TX load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/desc.h -->

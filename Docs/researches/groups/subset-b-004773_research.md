# subset-b-004773 research

Grouped research for the requested ath9k and carl9170 source files. Each section preserves the original source path and is bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg.h

## Purpose
`reg.h` is the central ath9k MAC/PCU hardware register map for non-USB ath9k devices. It contains register offsets, field masks, shifts, and helper address macros used by the HAL and core driver to program DMA, interrupts, TX/RX queues, beacon timers, sleep, counters, diagnostics, Bluetooth coexistence, WoW power-management bits, and PHY calibration control entry points that sit in MAC-visible register space.

## Important APIs, types, and constants
This header exports preprocessor constants rather than functions. Important groups include `AR_CR`, `AR_CFG`, `AR_IER`, `AR_ISR*`, and `AR_IMR*` for device control and interrupt status/masks; `AR_QTXDP`, `AR_QMISC`, `AR_DQCUMASK`, `AR_DLCL_IFS`, and related QCU/DCU macros for TX queue programming; `AR_RXDP`, `AR_HP_RXDP`, `AR_LP_RXDP`, `AR_RX_FILTER`, and multicast filter registers for RX control; `AR_TSF_*`, `AR_GEN_TIMERS`, `AR_TIMER_MODE`, beacon, quiet, sleep, and TSF registers for timekeeping; MIB/cycle/error counter addresses; key cache field definitions; PCU misc flags; Bluetooth coexistence weights and mode bits; and WoW/PM control fields such as `AR_PMCTRL_*` and `AR_WOW_BEACON_TIMO_MAX`.

## Control flow and integration
There is no executable control flow here. The macros are consumed by ath9k hardware routines through `REG_READ`, `REG_WRITE`, `REG_RMW_FIELD`, and bit operations from the ath9k HAL. The register families line up with higher-level files in this subset: `xmit.c` depends on TX queue/DCU/QCU behavior programmed through HAL helpers using these definitions, `wow.c` reaches PM/WoW routines that eventually touch the WoW and power-control fields, and `rng.c` uses PHY register definitions from companion PHY headers while following the same register-access convention.

## State and persistence behavior
The state represented by this file is volatile device state in PCI/SoC hardware registers. It controls persistent-in-hardware queue pointers, interrupt masks, timer state, TSF counters, sleep state, diagnostic overrides, and counters until reset, suspend, or explicit reprogramming. The header itself owns no software persistence.

## Dependencies
The macros assume ath9k hardware revision predicates and common register helpers are available from the surrounding HAL headers, especially `AR_SREV_*` selectors for revision-dependent offsets. Consumers must understand endian-neutral register values, field masks, and the distinction between read-clear interrupt registers and normal readable registers.

## Risks
The main risks are wrong offsets or masks causing silent hardware misprogramming, revision predicates selecting an invalid register layout, duplicate or aliased definitions hiding chip-specific differences, and callers using status/mask macros on the wrong register family. Interrupt and DMA definitions are particularly high risk because small mistakes can wedge TX/RX, lose interrupts, or leave DMA active during reset.

## Test signals
Useful signals include successful device probe/reset across supported revisions, stable TX/RX under interrupt load, correct queue setup and drain behavior, WoW suspend/resume tests, beacon/TSF timing tests, MIB counter sanity, and register-readback diagnostics where the HAL writes fields and verifies expected masked values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_aic.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_aic.h

## Purpose
`reg_aic.h` defines AR9003 adaptive interference cancellation register addresses and bit fields. It covers AIC control/status registers for both PHY chains, SRAM address/data windows, and a small set of Bluetooth coexistence PHY registers used to calibrate and monitor interference cancellation when WLAN and Bluetooth share RF resources.

## Important APIs, types, and constants
The file exports register offsets such as `AR_PHY_AIC_CTRL_0_B0`, `AR_PHY_AIC_STAT_0_B0`, `AR_PHY_AIC_SRAM_ADDR_B0`, and their B1-chain equivalents. Field masks and shifts describe monitor enable, calibration enable/reset, WLAN frequency, BT TX power thresholds, standby attenuation, RSSI min/max, radio delay, calibration convergence controls, monitor status, measurement counts, SRAM validity, attenuation entries, and isolation estimates.

## Control flow and integration
There is no executable code. AIC calibration and Bluetooth coexistence code uses these constants with PHY register read/modify/write helpers. The B0/B1 naming makes chain-specific programming explicit, while SRAM access macros support iterating over calibration entries through address/data registers.

## State and persistence behavior
All state is hardware-resident calibration and monitor state. Calibration status bits such as active/done/error reflect current hardware progress. SRAM fields hold AIC correction entries until cleared, recalibrated, or reset. The header does not persist anything in software.

## Dependencies
The offsets depend on `AR_SM_BASE`, `AR_SM1_BASE`, and `AR_AGC_BASE` from ath9k PHY register headers. Consumers must use the companion mask/shift macros consistently with `REG_RMW_FIELD`-style helpers.

## Risks
Risks center on incorrect chain selection, stale AIC SRAM contents, and misinterpreting signed/attenuation fields as plain unsigned values. Calibration done/error bits must be polled carefully to avoid enabling ineffective cancellation or blocking coexistence setup.

## Test signals
Relevant signals include successful AIC calibration completion, no calibration timeout/error bits, sane SRAM valid entries, improved coexistence throughput under Bluetooth activity, and no regression on devices without AIC support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_aic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_mci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_mci.h

## Purpose
`reg_mci.h` defines the MCI Bluetooth coexistence register interface used by ath9k chips with message-based WLAN/BT coordination. It maps MCI command, RX/TX control, scheduling, GPM buffers, interrupt, priority/frequency, LNA, gain, and debug registers.

## Important APIs, types, and constants
Key registers include `AR_MCI_COMMAND0..2`, `AR_MCI_RX_CTRL`, `AR_MCI_TX_CTRL`, `AR_MCI_GPM_*`, `AR_MCI_INTERRUPT_*`, `AR_MCI_REMOTE_CPU_INT*`, `AR_MCI_RX_STATUS`, `AR_MCI_CONT_STATUS`, `AR_BTCOEX_CTRL*`, `AR_BTCOEX_WL_WEIGHTS*`, `AR_BTCOEX_MAX_TXPWR`, and debug counter controls. Composite masks such as `AR_MCI_INTERRUPT_DEFAULT`, `AR_MCI_INTERRUPT_MSG_FAIL_MASK`, `AR_MCI_INTERRUPT_RX_HW_MSG_MASK`, and `AR_MCI_INTERRUPT_RX_MSG_DEFAULT` define the standard interrupt policy.

## Control flow and integration
The file has no direct control flow. Coexistence setup code programs message attributes, scheduling tables, interrupt enables, WLAN weights, BT priorities, gain controls, and remote CPU interrupts using these constants. The composite masks are the closest thing to policy: they select which MCI failures, received messages, and remote sleep updates should wake the driver.

## State and persistence behavior
MCI state persists in hardware while the coexistence block is active: command payloads, GPM pointers, schedule tables, interrupt enables/raw status, remote sleep state, continuous priority/RSSI state, coexistence weights, and debug counters. It is reset by MCI reset, device reset, or explicit reconfiguration.

## Dependencies
Consumers need ath9k register access helpers and Bluetooth coexistence state machines. Some fields are specific to AR9462-style MCI operation and require hardware capability checks before use.

## Risks
High-risk areas include interrupt-mask drift, not clearing message-fail conditions, stale GPM read/write pointers, incorrect LNA/shared-antenna policy, and wrong coexistence weights that either starve WLAN or break Bluetooth. The fail-mask macros are critical for robust recovery paths.

## Test signals
Signals include MCI interrupt handling under BT traffic, remote sleep/wake updates, GPM message parsing, coexistence throughput with concurrent WLAN/BT use, absence of repeated message-fail interrupts, and stable reset/reinitialization after BT controller resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_mci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_wow.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_wow.h

## Purpose
`reg_wow.h` is the ath9k Wake-on-Wireless register definition header. It defines pattern memory, pattern-length registers, wake status bits, keep-alive and beacon-miss controls, software WoW control bits, transmit-buffer windows, and supported pattern masks used by the hardware WoW implementation.

## Important APIs, types, and constants
Important definitions include `AR_WOW_PATTERN`, `AR_WOW_COUNT`, `AR_WOW_BCN_EN`, `AR_WOW_BCN_TIMO`, `AR_WOW_KEEP_ALIVE*`, `AR_WOW_PATTERN_MATCH`, `AR_WOW_LENGTH1..4`, `AR_SW_WOW_CONTROL`, wake enable/status bits such as `AR_WOW_MAGIC_EN`, `AR_WOW_PATTERN_EN`, `AR_WOW_MAGIC_PAT_FOUND`, `AR_WOW_KEEP_ALIVE_FAIL`, and `AR_WOW_BEACON_FAIL`, plus `AR_WOW_TB_PATTERN`, `AR_WOW_TB_MASK`, and length-mask helpers for 16 patterns.

## Control flow and integration
No functions are defined. HAL WoW routines use the masks to write packet patterns and masks into transmit-buffer memory, set length fields, enable magic/user/beacon/keepalive wake sources, and clear wake events during resume. `wow.c` maps cfg80211 triggers into HAL-level WoW trigger bits that eventually use these register definitions.

## State and persistence behavior
WoW state persists in low-power hardware while the host sleeps. Pattern contents, masks, enable bits, keepalive timers, beacon miss thresholds, and wake status bits remain relevant across suspend until resume clears or reinitializes them.

## Dependencies
This header depends on ath9k HAL WoW code for interpretation. The file assumes pattern count and size constants from the driver/HAL and must be matched to chip generation because legacy devices support fewer patterns than newer ones.

## Risks
Risks include incorrect pattern length packing, enabling unsupported pattern slots, failing to clear stale wake status, and mismatched mask semantics that cause false wakes or missed disassociation/magic-packet wakes. Because these registers operate during system sleep, failures can be hard to diagnose after resume.

## Test signals
Test signals include suspend with magic packet, user pattern, beacon miss, and deauth/disassoc wake triggers; validating wake reason bits on resume; repeated suspend/resume cycles; and ensuring unsupported pattern slots are not exposed through wiphy WoW capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_wow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/rng.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/rng.c

## Purpose
`rng.c` exposes supported ath9k AR9300-generation devices as Linux `hwrng` providers. It samples ADC/PHY observation registers, filters repeated or sentinel values, and registers a device-managed random source with the kernel.

## Important APIs, types, and functions
`ath9k_rng_start()` names and registers `sc->rng_ops` for AR9300 2.0 or later devices, with `quality = 320`. `ath9k_rng_stop()` unregisters it. `ath9k_rng_read()` implements the `struct hwrng` read callback with optional blocking/retry behavior. `ath9k_rng_data_read()` wakes the device, selects PHY observation sources, reads `AR_PHY_TST_ADC`, filters invalid pairs, updates `sc->rng_last`, and returns bytes produced. `ath9k_rng_delay_get()` backs off after repeated empty reads.

## Control flow and integration
Startup is called from ath9k device initialization and is skipped for old revisions or already registered RNGs. Reads enter through the hwrng core, wake the hardware using ath9k power-save helpers, configure observation muxes, sample pairs into 32-bit words, restore power state, and return either produced bytes or `-EIO` if a blocking read repeatedly fails. Registration uses `devm_hwrng_register`, while stop explicitly unregisters if active.

## State and persistence behavior
The persistent software state is `sc->rng_ops.read`, `sc->rng_name`, and `sc->rng_last`. `rng_last` suppresses duplicate sample reuse across reads. Hardware observation mux state is changed for sampling but not stored by this file beyond register writes.

## Dependencies
The file depends on Linux `hw_random`, ath9k power management, `ath9k.h`, `hw.h`, and AR9003 PHY register definitions. It relies on `REG_READ`, `REG_RMW_FIELD`, and `REG_CLR_BIT`.

## Risks
Risks include low entropy under poor RF/ADC conditions, repeated empty reads causing latency, interaction with PHY observation state used by diagnostics, and assuming AR9300 ADC behavior across all supported revisions. The warning in carl9170's RNG Kconfig does not apply directly, but any hardware RNG over device buses should still be treated conservatively.

## Test signals
Signals include hwrng registration visibility, successful reads with nonzero byte counts, no power-save imbalance, no repeated `-EIO` under normal RF conditions, entropy health tests in the hwrng framework, and suspend/remove paths leaving no registered callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/tx99.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/tx99.c

## Purpose
`tx99.c` implements ath9k debugfs support for continuous transmit test mode. TX99 builds a synthetic PN9 data frame, stops normal traffic/reception, forces TX power, and sends a self-linked transmit descriptor stream for regulatory/lab testing.

## Important APIs, types, and functions
`ath9k_tx99_init_debug()` creates `tx99` and `tx99_power` debugfs files on supported hardware. `write_file_tx99()` parses a boolean to start, stop, or reset TX99 under `sc->mutex`. `ath9k_tx99_init()` builds the SKB, resets hardware, disables interrupts, drains TX queues, stops receive, stops mac80211 queues, sets `sc->tx99_state`, applies power, and calls `ath9k_tx99_send()` from `xmit.c`. `ath9k_tx99_stop()` drains TX, restarts RX, restores interrupts/queues, frees `sc->tx99_skb`, clears state, and tells hardware to stop TX99. `write_file_tx99_power()` validates and applies half-dBm power units.

## Control flow and integration
Userspace controls the mode through debugfs. Start rejects invalid driver state and multi-vif operation, allocates a 1200-byte frame addressed to the permanent MAC, configures no-ACK and optional MCS/HT40 flags, then leaves hardware awake for continuous transmit. Stop goes through `ath9k_tx99_deinit()`, which resets and then stops TX99 while holding the device awake.

## State and persistence behavior
TX99 state lives in `sc->tx99_state`, `sc->tx99_skb`, `sc->tx99_power`, and optionally `sc->tx99_vif`. It persists until the debugfs file is written false, reset/reinit occurs, or device removal frees state. It intentionally disrupts normal RX/TX while active.

## Dependencies
The file depends on ath9k debugfs, reset, power-save, queue drain, RX start/stop, interrupt control, `ath9k_hw_tx99_*` HAL routines, and `ath9k_tx99_send()` in `xmit.c`. It is compiled only with TX99 support.

## Risks
Risks include leaving hardware awake or queues stopped on an error path, leaking or double-freeing `tx99_skb`, using TX99 on multi-vif channels, and invalid transmit power changes during active continuous transmit. Because this is a lab mode, accidental enablement can disrupt normal network operation.

## Test signals
Signals include debugfs file creation only on supported revisions, start/stop cycles restoring queues and RX, continuous RF output at requested power, correct rejection of multi-vif or invalid state, and no SKB leak after reset/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/tx99.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wmi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wmi.c

## Purpose
`wmi.c` implements the WMI control channel for ath9k_htc USB devices. It sends serialized commands over an HTC endpoint, waits for matching responses, queues asynchronous firmware events, and dispatches events such as SWBA, fatal reset, and TX status.

## Important APIs, types, and functions
`ath9k_init_wmi()` allocates `struct wmi`, initializes queues, locks, completions, pending event lists, and the tasklet. `ath9k_wmi_connect()` binds WMI callbacks to `WMI_CONTROL_SVC` through HTC. `ath9k_wmi_cmd()` builds an SKB with HTC/WMI headroom, serializes command issue under `op_mutex`, waits on `cmd_wait`, and handles timeout by invalidating `last_seq_id`. `ath9k_wmi_ctrl_rx()` distinguishes events from responses, validates sequence numbers, and schedules the tasklet. `ath9k_wmi_event_tasklet()` drains queued events and dispatches them. `ath9k_stop_wmi()`, `ath9k_destroy_wmi()`, and `ath9k_wmi_event_drain()` stop and clean up state.

## Control flow and integration
Command flow is synchronous: allocate SKB, reserve header room, copy payload, lock operations, reject stopped WMI, push `wmi_cmd_hdr`, increment `tx_seq_id`, record response buffer and sequence, send via HTC, and wait for completion. RX flow is asynchronous from HTC callbacks. Event IDs have bit `0x1000` and are queued for tasklet context; normal responses must match `last_seq_id` before copying response bytes and completing the waiter.

## State and persistence behavior
Persistent WMI state includes `stopped`, HTC endpoint ID, sequence counters, response buffer pointers, event SKB queue, tasklet, locks, and pending TX event list. State lasts for the lifetime of the ath9k_htc private structure and is torn down at device stop/destroy.

## Dependencies
The file depends on `htc.h`, the HTC service layer, ath9k_htc reset/TX/SWBA handlers, Linux SKB queues, tasklets, completions, spinlocks, and mutexes. It uses command IDs and event structs from `wmi.h`.

## Risks
Risks include response timeout races, stale `cmd_rsp_buf`/length if firmware sends malformed responses, sequence wrap or mismatch dropping valid responses, event queue growth if tasklets are blocked, and locking mistakes between HTC callback context and command waiters. Event handling also deliberately ignores events before `priv->initialized`, which must align with probe ordering.

## Test signals
Signals include successful firmware version and register commands, timeout behavior on unplug, correct fatal-event reset work scheduling, TX status delivery under load, no SKB leaks after event drain, and no command execution after `ath9k_stop_wmi()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wmi.h

## Purpose
`wmi.h` declares the ath9k_htc WMI protocol structures, command/event IDs, driver-side WMI state, and helper macros for issuing common commands. It is the contract between host driver code and target firmware for the HTC WMI control service.

## Important APIs, types, and constants
Protocol structs include `wmi_cmd_hdr`, `wmi_fw_version`, `wmi_event_swba`, `wmi_event_txstatus`, `register_write`, and `register_rmw`. Command IDs cover firmware version, interrupts, init, TX/RX control, VAP/node operations, register read/write/RMW, rate-control updates, stats, and bitrate masks. Event IDs cover target-ready, SWBA, fatal, timeout/beacon miss/delba, and TX status. `struct wmi` stores HTC endpoint state, locks, completion, sequence counters, event queue/tasklet, pending TX events, stopped flag, and multi-write/RMW batching buffers.

## Control flow and integration
The header provides declarations implemented in `wmi.c` and two command macros, `WMI_CMD` and `WMI_CMD_BUF`, that call `ath9k_wmi_cmd()` with a conventional response buffer and two-second timeout. Other ath9k_htc code includes this header to send firmware commands and interpret WMI events.

## State and persistence behavior
`struct wmi` is long-lived per USB device. It persists command sequencing, queued events, locks, and batching arrays across individual commands. The multi-write and multi-RMW counters/indexes support batching multiple register operations before sending to firmware.

## Dependencies
The file depends on ath9k_htc private types, HTC endpoint IDs, Linux SKBs/list/spinlock/mutex/completion primitives, and firmware command payload layout. Endianness annotations are part of the wire contract.

## Risks
Risks include host/firmware ABI drift, packed-structure size changes, wrong endian conversion, overflow of `MAX_CMD_NUMBER` or `MAX_RMW_CMD_NUMBER` batching arrays, and assuming event payload lengths without validating received SKB lengths in consumers.

## Test signals
Signals include build-time structure compatibility, firmware command smoke tests, multi-register read/write/RMW tests, TX status parsing, event dispatch coverage, and timeout/unplug handling with no use-after-free of `struct wmi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wow.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wow.c

## Purpose
`wow.c` connects cfg80211/mac80211 Wake-on-Wireless support to ath9k hardware. It advertises supported triggers, programs default deauth/disassoc and user packet patterns, enters low-power WoW mode on suspend, restores interrupts/work on resume, and configures device wakeup capability.

## Important APIs, types, and functions
`ath9k_init_wow()` publishes `wiphy->wowlan` capabilities when PCI WoW or `force_wow` is enabled, selecting legacy or newer pattern count by chip revision. `ath9k_suspend()` is the main suspend entry point. `ath9k_resume()` restores interrupts and calls `ath9k_hw_wow_wakeup()`. `ath9k_set_wakeup()` toggles device wakeup. Helpers include `ath9k_wow_map_triggers()`, `ath9k_wow_add_disassoc_deauth_pattern()`, and `ath9k_wow_add_pattern()`.

## Control flow and integration
Suspend deinitializes channel context, locks `sc->mutex`, rejects invalid devices, missing triggers, multi-vif, multi-channel, or unassociated STA state, maps triggers, cancels work/ANI, wakes hardware, stops BT coexistence, programs mandatory deauth/disassoc patterns in slots 0 and 1, programs user patterns starting at slot 2, saves the old interrupt mask, enables only beacon-miss/global interrupts for sleep, synchronizes IRQ/tasklet shutdown, enables hardware WoW, restores power-save, and sets `ATH_OP_WOW_ENABLED`. Resume wakes hardware, restores `wow_intr_before_sleep`, obtains wake status, restarts work and BT coexistence, clears the WoW flag, and restores power-save.

## State and persistence behavior
Software state includes `sc->wow_intr_before_sleep`, `ATH_OP_WOW_ENABLED`, device wakeup enablement, and wiphy WoW capability pointers. Hardware state includes pattern slots, trigger enables, interrupt masks, and wake status across suspend.

## Dependencies
The file depends on cfg80211 WoW structs, mac80211 suspend/resume hooks, ath9k HAL WoW functions, interrupt/tasklet synchronization, power-save helpers, BT coexistence start/stop, and current BSSID state in `ath_common`.

## Risks
Risks include false wakes from broad masks, missed wakes if pattern/mask construction is wrong, failure paths after work/BT coexistence have been stopped, suspend returning `1` for unsupported runtime conditions, and lack of multi-vif/multi-channel WoW support. Pattern slots 0 and 1 are reserved for disconnect detection, so user pattern accounting must stay aligned with advertised capabilities.

## Test signals
Signals include cfg80211 WoW capability visibility, suspend rejection for unsupported states, magic packet wake, user pattern wake, deauth/disassoc wake, beacon miss wake, restored interrupt masks after resume, and no lost network work/BT coexistence after repeated cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/xmit.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/xmit.c

## Purpose
`xmit.c` is the main ath9k transmit engine. It bridges mac80211 TXQs to ath9k hardware descriptors, implements AMPDU aggregation and BlockAck window management, handles DMA queueing and completion for legacy DMA and EDMA, reports TX status/airtime/rate-control feedback, supports power-save buffered frame release, and provides the TX99 send path.

## Important APIs, types, and functions
External entry points include `ath9k_wake_tx_queue()`, `ath_tx_aggr_start()`, `ath_tx_aggr_stop()`, `ath_tx_aggr_sleep()`, `ath_tx_aggr_wakeup()`, `ath9k_release_buffered_frames()`, `ath_txq_setup()`, `ath_txq_update()`, `ath_cabq_update()`, `ath_draintxq()`, `ath_drain_all_txq()`, `ath_tx_cleanupq()`, `ath_txq_schedule()`, `ath_txq_schedule_all()`, `ath_tx_start()`, `ath_tx_cabq()`, `ath_tx_tasklet()`, `ath_tx_edma_tasklet()`, `ath_tx_init()`, `ath_tx_node_init()`, `ath_tx_node_cleanup()`, and `ath9k_tx99_send()`. Important internal helpers include `ath_tx_prepare()`, `ath_tx_setup_buffer()`, `ath_tx_fill_desc()`, `ath_buf_set_rate()`, `ath_tx_sched_aggr()`, `ath_tx_form_aggr()`, `ath_tx_complete_aggr()`, `ath_tx_process_buffer()`, `ath_tx_complete_buf()`, and `ath_tx_rc_status()`.

## Control flow and integration
Normal TX starts in mac80211 with `ath_tx_start()` or TXQ scheduling. Frames are prepared by assigning sequence numbers, adding hardware alignment padding, computing frame metadata, mapping DMA, merging rate tables, filling hardware descriptors, and linking descriptors into a hardware TX queue. TXQ scheduling pulls SKBs from mac80211 TXQs through `ieee80211_tx_dequeue()`, forms either short bursts or aggregates, respects queue depth limits, and adds descriptors to DMA. Completion tasklets poll hardware TX status, handle descriptor holding/stale races, process non-aggregate or aggregate results, update airtime/rate-control status, retry unacked aggregate subframes, send BARs when the BlockAck window advances past failures, and queue final SKB status back to mac80211 after dropping the queue lock.

## State and persistence behavior
Persistent transmit state is spread across `sc->tx`, per-queue `struct ath_txq`, per-node/per-TID `struct ath_atx_tid`, per-frame `struct ath_frame_info`, and hardware descriptors. Key state includes free descriptor lists, DMA addresses, queue depth and AMPDU depth, pending frame counts, retry queues, BlockAck window head/tail bitmap, TID sequence counters, BAR index, power-save filter flags, EDMA FIFO indices, and completion queues. Hardware state persists in TX descriptors, TXDP registers/FIFOs, TX status rings, and DMA engine state until completion, drain, or reset.

## Dependencies
The file depends heavily on mac80211 TXQ, STA, rate-control, airtime, UAPSD, and BlockAck APIs; Linux DMA mapping; ath9k HAL descriptor/TX queue/status functions; ath9k debug/stat/reset/power-save helpers; beacon and channel-context code; Bluetooth coexistence aggregation limits; dynack; PAPRD; and TX99 debug support.

## Risks
This file is concurrency and hardware-state sensitive. Risks include DMA leaks on setup or completion errors, queue lock misuse around mac80211 callbacks, BlockAck window corruption, retry queue ordering bugs, stale descriptor handling races, EDMA FIFO desynchronization, incorrect padding restoration for status SKBs, queue depth underflow, BAR storms, power-save buffered-frame state drift, and reset races while tasklets process completions. Rate/power descriptor programming must also stay aligned with hardware revisions and regulatory limits.

## Test signals
Signals include sustained TCP/UDP throughput, AMPDU start/stop/retry correctness, BlockAck and BAR behavior under packet loss, no TX stalls after queue drain/reset, EDMA and legacy DMA coverage, mac80211 TX status correctness, airtime accounting, UAPSD release/EOSP tests, beacon CABQ delivery, PAPRD completion, TX99 operation, DMA debug clean runs, and stress with station sleep/wake and channel reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/xmit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/Kconfig

## Purpose
`Kconfig` defines build-time configuration for the carl9170 USB 802.11n driver and optional features. It exposes the main driver, LED support, debugfs, WPS push-button input support, and hardware RNG support.

## Important APIs, types, and options
`CONFIG_CARL9170` is a tristate depending on `USB` and `MAC80211`, selecting `ATH_COMMON`, `FW_LOADER`, and `CRC32`. `CONFIG_CARL9170_LEDS` defaults to enabled when mac80211 LED support exists. `CONFIG_CARL9170_DEBUGFS` depends on debugfs and mac80211 debugfs and defaults off. `CONFIG_CARL9170_WPC` is an internal bool tied to input support. `CONFIG_CARL9170_HWRNG` optionally exposes the firmware/device RNG with a transport eavesdropping warning.

## Control flow and integration
There is no runtime control flow. These symbols drive conditional compilation in the Makefile and driver headers, selecting optional fields and objects such as debugfs and LED code. The main help text documents the required `carl9170-1.fw` firmware.

## State and persistence behavior
State is build configuration only. Choices persist in the kernel `.config` and determine which code and struct fields exist in the built module.

## Dependencies
The configuration depends on kernel USB, mac80211, debugfs, LED, input, firmware loader, CRC32, and hwrng subsystems.

## Risks
Risks include enabling `CARL9170_HWRNG` without accepting USB transport observability, building the driver without required firmware availability, and optional feature dependencies changing struct layout or code paths. Debugfs defaults off, which can surprise diagnostics users.

## Test signals
Signals include Kconfig dependency resolution for built-in and module builds, module name `carl9170`, firmware request behavior, LED/debugfs/HWRNG symbols compiling in all valid combinations, and no unresolved references when optional subsystems are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/Makefile

## Purpose
`Makefile` defines the object composition for the carl9170 kernel module. It lists the core compilation units and conditionally adds debugfs support.

## Important APIs, types, and targets
`carl9170-objs` includes `main.o`, `usb.o`, `cmd.o`, `mac.o`, `phy.o`, `led.o`, `fw.o`, `tx.o`, and `rx.o`. `carl9170-$(CONFIG_CARL9170_DEBUGFS)` adds `debug.o`. `obj-$(CONFIG_CARL9170)` emits `carl9170.o`.

## Control flow and integration
There is no runtime control flow. Kbuild combines the listed objects into the module or built-in object based on `CONFIG_CARL9170`, with debug object inclusion controlled by the Kconfig symbol.

## State and persistence behavior
The file encodes build graph state only. It does not affect runtime state except by including or excluding compiled objects.

## Dependencies
It depends on Kbuild conventions and symbol values produced by `Kconfig`. The object list must match source files and exported prototypes in `carl9170.h`.

## Risks
Risks include stale object lists after source moves, unconditional inclusion of feature-specific code that should be conditional, and missing object inclusion causing unresolved symbols. `led.o` is always compiled, so the LED source must guard optional LED subsystem use internally.

## Test signals
Signals include allmodconfig/allyesconfig builds, `CONFIG_CARL9170=m/y/n` behavior, `CONFIG_CARL9170_DEBUGFS` toggling `debug.o`, and no missing symbol or dead object references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/carl9170.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/carl9170.h

## Purpose
`carl9170.h` is the central private header for the carl9170 driver. It defines driver constants, device state, aggregation/TID bookkeeping, the main `struct ar9170`, optional feature fields, state helpers, and cross-file function prototypes for USB, MAC, RX/TX, LED, PHY, firmware, and power-save code.

## Important APIs, types, and constants
Key definitions include `CARL9170FW_NAME`, `PAYLOAD_MAX`, queue/timeout constants, TID sequence helpers, `enum carl9170_device_state`, `enum carl9170_tid_state`, restart reasons, ERP modes, `struct carl9170_sta_tid`, `struct carl9170_tx_queue_stats`, `struct carl9170_vif_info`, optional `struct carl9170_led`, the large `struct ar9170`, `struct carl9170_sta_info`, and `struct carl9170_tx_info`. Inline helpers include `ar9170_qmap()`, state predicates such as `IS_ACCEPTING_CMD()`, state setters, header/TID/sequence extraction helpers, and main-vif lookup helpers.

## Control flow and integration
The header has mostly declarations and inline helpers. Runtime modules include it to access shared driver state: `cmd.c` uses `cmd_buf`, state predicates, and command buffers; USB code owns command execution and URBs; TX/RX code manages queues, AMPDU state, and status; MAC/PHY code programs hardware; firmware code fills `ar->fw`; optional debugfs/LED/HWRNG/WPS code compiles fields under Kconfig guards.

## State and persistence behavior
`struct ar9170` is the persistent per-device state. It holds common ath/mac80211 state, USB anchors and tasklet counters, firmware descriptors/settings, reset work, interface/beacon/filter/crypto/PHY state, survey/tally data, calibration power tables, TX queues and AMPDU state, command synchronization state, EEPROM, RX merge state, BAR queues, optional WPS/debugfs/HWRNG/LED state, power-save state, and a flexible command/response buffer union. It persists from allocation through unregister/free.

## Dependencies
The header depends on Linux kernel, firmware, completion, spinlock, USB, cfg80211/mac80211, optional LED/input/hwrng subsystems, carl9170 firmware/hardware protocol headers, EEPROM, and ath regulatory support.

## Risks
Risks include lock-order bugs across the many state domains, struct layout changes under optional configs, stale state predicates allowing commands during teardown, flexible-array union misuse, RCU misuse around vif/TID pointers, and queue/accounting drift across reset paths. Because many files share this header, changes have wide blast radius.

## Test signals
Signals include compile coverage for optional configs, probe/remove/reset cycles, firmware parse and boot, command timeout recovery, TX/RX stress, AMPDU sleep/wake behavior, power-save transitions, debugfs/LED/WPS/HWRNG feature tests, and lockdep/KASAN/RCU diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/carl9170.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/cmd.c

## Purpose
`cmd.c` implements basic carl9170 firmware command helpers: register read/write, echo testing, command buffer allocation, reboot/reset, beacon control, tally collection, and firmware power-save commands.

## Important APIs, types, and functions
`carl9170_write_reg()` sends `CARL9170_CMD_WREG`. `carl9170_read_mreg()` and `carl9170_read_reg()` send `CARL9170_CMD_RREG` and convert little-endian responses. `carl9170_echo_test()` validates command roundtrip. `carl9170_cmd_buf()` allocates a `struct carl9170_cmd` and initializes header fields. `carl9170_reboot()` sends async reboot, `carl9170_mac_reset()` sends software reset, `carl9170_bcn_ctrl()` sends async beacon control, `carl9170_collect_tally()` updates driver and survey counters from firmware, and `carl9170_powersave()` sends async PSM state.

## Control flow and integration
Most helpers package little-endian payloads and call `carl9170_exec_cmd()` synchronously or `__carl9170_exec_cmd(..., true)` for allocated async command buffers. Error paths rate-limit logging for register access. Tally collection divides firmware active/CCA/TX times by firmware tick, accumulates counters, and updates the current channel's `survey_info` in milliseconds using `do_div`.

## State and persistence behavior
Register helpers do not keep state locally, but they mutate device registers through firmware. `carl9170_collect_tally()` persists cumulative values in `ar->tally` and current-channel `ar->survey[]`. `carl9170_powersave()` changes firmware PSM state. Command buffers are short-lived and freed by the lower execution path when requested.

## Dependencies
The file depends on `carl9170.h`, `cmd.h`, firmware command IDs and payload structs, USB command execution, mac80211 survey structures, endian conversion, and `net_ratelimit()` diagnostics.

## Risks
Risks include abusing the output buffer as the register-offset input buffer in `carl9170_read_mreg()` when callers provide overlapping or undersized storage, endian mistakes, command execution after device teardown, incorrect tally unit conversion, and async command allocation failures. The register-write batching macros in `cmd.h` rely on these primitives.

## Test signals
Signals include echo test success, single and multi-register read/write readback, software reset/reboot behavior, beacon control effects, survey/tally updates under traffic, powersave transitions around beacons, and command timeout/restart handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/cmd.h

## Purpose
`cmd.h` declares carl9170 command helper APIs and defines macro-based batching helpers for synchronous and asynchronous register writes. It is the command access interface used by MAC/PHY/setup code to program firmware-controlled hardware registers.

## Important APIs, types, and macros
Declarations cover register read/write, echo, reboot, MAC reset, powersave, tally, beacon control, and command buffer allocation. Inline helpers include `carl9170_flush_cab()` and `carl9170_rx_filter()`. Synchronous batching uses `carl9170_regwrite_begin`, `carl9170_regwrite`, `carl9170_regwrite_finish`, and `carl9170_regwrite_result`. Async batching uses `carl9170_async_regwrite_begin`, `carl9170_async_regwrite`, `carl9170_async_regwrite_flush`, `carl9170_async_regwrite_finish`, and `carl9170_async_regwrite_result`.

## Control flow and integration
The batching macros open a scoped `do { ... } while (0)` block with hidden locals. They accumulate register/value pairs in `ar->cmd_buf` or an allocated async `struct carl9170_cmd`, flush when the payload reaches `PAYLOAD_MAX / 2` pairs, stop if `IS_ACCEPTING_CMD()` fails, and expose the final error through the result macro. Async flush transfers ownership to `__carl9170_exec_cmd()` and allocates a new buffer when needed.

## State and persistence behavior
Synchronous batching temporarily uses the per-device `ar->cmd_buf` union. Async batching temporarily owns heap command buffers. The persistent effect is the firmware/hardware register state changed by successful write commands. No standalone state is stored in this header.

## Dependencies
The header depends on `carl9170.h`, firmware command IDs and payload layouts, `PAYLOAD_MAX`, `CARL9170_MAX_CMD_PAYLOAD_LEN`, `IS_ACCEPTING_CMD()`, and command execution functions.

## Risks
Macro scope and hidden local names make misuse easy: callers must pair begin/finish/result correctly, cannot safely nest these macros, and must avoid control-flow surprises around labels. Async batching must avoid double-free after ownership transfer; synchronous batching assumes exclusive safe use of `ar->cmd_buf` in the current context. Failing `IS_ACCEPTING_CMD()` can silently skip remaining writes except for the returned error state.

## Test signals
Signals include register programming sequences longer than one payload, async and sync flush boundary tests, teardown-time command rejection, memory leak checks for async allocation/failure paths, and readback of configured MAC/PHY registers after batched writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/cmd.h -->

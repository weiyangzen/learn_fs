# subset-b-004766 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_mci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_mci.c

## Purpose
`ar9003_mci.c` implements the AR9003 MCI hardware side of Bluetooth coexistence for ath9k. It drives the WLAN-to-BT mailbox protocol, generic payload message (GPM) ring handling, Bluetooth sleep/wake/reset handshakes, calibration arbitration, 2 GHz/5 GHz coexistence flag switching, interrupt snapshotting, and the MCI reset/cleanup sequence. The file is register-centric and is only fully useful on chip families that expose the MCI coexistence block, especially AR9462/AR9565-class devices.

## Important APIs, Types, and Functions
The exported APIs are `ar9003_mci_setup()`, `ar9003_mci_cleanup()`, `ar9003_mci_send_message()`, `ar9003_mci_state()`, `ar9003_mci_get_interrupt()`, `ar9003_mci_get_next_gpm_offset()`, `ar9003_mci_set_bt_version()`, and `ar9003_mci_send_wlan_channels()`. The CONFIG-gated hardware reset/calibration entry points declared in the header are implemented here as well: `ar9003_mci_start_reset()`, `ar9003_mci_end_reset()`, `ar9003_mci_reset()`, `ar9003_mci_stop_bt()`, `ar9003_mci_init_cal_req()`, `ar9003_mci_init_cal_done()`, `ar9003_mci_2g5g_switch()`, `ar9003_mci_check_bt()`, `ar9003_mci_get_isr()`, `ar9003_mci_bt_gain_ctrl()`, `ar9003_mci_set_power_awake()`, and `ar9003_mci_check_gpm_offset()`.

Most state is carried by `ah->btcoex_hw.mci` (`struct ath9k_hw_mci` in `btcoex.h`): interrupt accumulators, DMA addresses, GPM buffer pointer/length/index, WLAN channel bitmap, calibration sequence counters, MCI configuration bits, BT state, version knowledge, pending query/flush flags, 2G/5G update flags, and recovery timestamps. The file depends heavily on register macros from `reg.h`, MCI definitions from `ar9003_mci.h`, PHY definitions from `ar9003_phy.h`, and AIC operations from `ar9003_aic.h`.

## Control Flow
`ar9003_mci_setup()` stores the GPM DMA address, buffer, length, and schedule-table address, then invokes `ar9003_mci_reset()` with interrupts enabled and a full-sleep style setup. `ar9003_mci_reset()` programs the GPM/schedule registers, writes chip-specific BT coexistence control values, configures OSLA/stat/debug behavior, resets MCI TX/RX paths, checks pending GPM offsets before RX reset, initializes the cached GPM pointer, enables or disables LNA updates depending on antenna sharing, sets optional observation GPIOs, marks MCI ready, runs `ar9003_mci_prep_interface()`, optionally enables MCI interrupts, and starts AIC normal mode when enabled.

`ar9003_mci_prep_interface()` performs the remote BT reset/wake handshake. It masks MCI interrupts, clears pending raw bits, sends `MCI_REMOTE_RESET` and `MCI_REQ_WAKE`, waits for `SYS_WAKING`, marks BT awake on success, sends WLAN `SYS_WAKING`, adjusts BT priority interrupts, handles shared LNA transfer in 2 GHz, clears redundant wake notifications, and restores the saved interrupt mask. Lower-level helpers such as `ar9003_mci_wait_for_interrupt()` poll raw interrupt bits, acknowledge them, and perform special side effects for `REQ_WAKE`, `SYS_SLEEPING`, and `SYS_WAKING`.

Message transmission flows through `ar9003_mci_send_message()`. It refuses to send when the BTCOEX/MCI mode register is invalid or disabled, or when `check_bt` is requested and BT is asleep. In those cases it calls `ar9003_mci_queue_unsent_gpm()` so important coex GPM requests can be retried. On a valid send it optionally disables interrupts, clears `SW_MSG_DONE`/failure bits, writes payload words, writes `AR_MCI_COMMAND0`, waits for completion, updates pending flags based on success, and restores the interrupt enable register.

GPM receive flow is split between `ar9003_mci_get_next_gpm_offset()` and `ar9003_mci_wait_for_gpm()`. The offset function clears the GPM interrupt bit, compares the hardware write pointer with the cached `gpm_idx`, walks the circular buffer, skips reserved/recycled entries, returns byte offsets, and reports whether more messages are pending. `ar9003_mci_wait_for_gpm()` waits for a requested calibration or coex-agent GPM, recycles consumed entries, responds to BT calibration requests while waiting for calibration grants, processes unrelated coex-agent messages, and drains remaining queued messages.

## State and Persistence Behavior
No persistent storage is written. State persists only in `struct ath_hw`, `struct ath9k_hw_mci`, hardware registers, and the DMA-backed GPM buffer. Important durable-in-runtime fields include `ready`, `bt_state`, `gpm_idx`, `query_bt`, `need_flush_btinfo`, `update_2g5g`, `wlan_channels_update`, `unhalt_bt_gpm`, `halted_bt_gpm`, version fields, and calibration sequence counters. Interrupts are latched into `mci->raw_intr` and `mci->rx_msg_intr` by `ar9003_mci_get_isr()` and atomically cleared for callers by `ar9003_mci_get_interrupt()`.

## Dependencies and Integration Points
Reset integration is in `hw.c`: the core reset path calls MCI start/end reset around calibration, checks GPM offset before warm reset, stops BT on reset/sleep transitions, reruns MCI reset after core hardware reset, and calls `ar9003_mci_check_bt()` afterward. Calibration integration is in `ar9003_calib.c` through `ar9003_mci_init_cal_req()` and `ar9003_mci_init_cal_done()`. Runtime MCI driver integration is in `mci.c`, which uses message sending, interrupt retrieval, state queries, version/channel updates, and setup/cleanup. ISR integration is in `ar9003_mac.c`, which calls `ar9003_mci_get_isr()`. The GPIO coexistence path calls `MCI_STATE_NEED_FTP_STOMP`, and WoW code queries `MCI_STATE_GET_WLAN_PS_STATE`.

## Risks
The code is sensitive to register sequencing and timing delays. Failed waits can leave pending coex updates queued, and any GPM index mismatch forces BT info requery. The state switch in `ar9003_mci_state()` defines many enum cases in the header but implements only a subset; unhandled state queries return zero, which is meaningful for callers such as WoW because zero maps to `MCI_PS_DISABLE`. `ar9003_mci_get_max_txpower()` returns `-1` through a `u16`, so users must treat it as an unsigned sentinel rather than a normal power value. The GPM buffer is treated as a packed hardware-owned ring and uses manual byte offsets, so bad length/index values can corrupt interpretation. Interrupt masking during synchronous sends avoids reentry but can hide ordering bugs if callers hold other driver locks.

## Test Signals
Useful test signals are MCI debug logs for reset/wake/version/calibration handshakes, absence of timeout logs in `ar9003_mci_wait_for_interrupt()`/`ar9003_mci_wait_for_gpm()`, correct `ATH9K_INT_MCI` delivery and raw/rx bit clearing, stable `gpm_idx` across resets, successful BT calibration grant/done exchange during hardware calibration, WLAN channel bitmap messages after channel changes, and clean suspend/resume/full-sleep behavior with `halted_bt_gpm` and `unhalt_bt_gpm` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_mci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_mci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_mci.h

## Purpose
`ar9003_mci.h` is the protocol contract for AR9003 MCI Bluetooth coexistence. It defines the MCI message headers, coex-agent GPM layout, calibration message subtypes, BT state values, state-query IDs, configuration bitfields, antenna architecture encodings, helper macros for packed GPM payloads, and public function prototypes.

## Important APIs, Types, and Defines
Important enums include `mci_message_header`, `mci_gpm_subtype`, `mci_bt_state`, `mci_ps_state`, `mci_state_type`, `mci_gpm_coex_opcode`, `mci_gpm_coex_query_type`, `mci_gpm_coex_halt_bt_gpm`, and `mci_gpm_coex_bt_update_flags_op`. The header also defines coex profile IDs and GPM byte offsets for version, status query, WLAN channels, profile info, status update, and BT flag update messages.

Key macros are `MCI_GPM_TYPE()`, `MCI_GPM_OPCODE()`, `MCI_GPM_SET_CAL_TYPE()`, `MCI_GPM_SET_TYPE_OPCODE()`, `MCI_GPM_RECYCLE()`, and `MCI_GPM_IS_CAL_TYPE()`. Configuration bits such as `ATH_MCI_CONFIG_DISABLE_MCI`, `ATH_MCI_CONFIG_DISABLE_MCI_CAL`, `ATH_MCI_CONFIG_DISABLE_OSLA`, `ATH_MCI_CONFIG_DISABLE_FTP_STOMP`, `ATH_MCI_CONFIG_CONCUR_TX`, `ATH_MCI_CONFIG_ANT_ARCH`, and debug/observation flags drive behavior in `ar9003_mci.c`.

## Control Flow
The header itself has no runtime control flow, but it defines the inputs that drive the implementation. Callers use the always-declared MCI core functions for message send, setup, cleanup, interrupt retrieval, GPM walking, BT version updates, and WLAN channel publishing. Under `CONFIG_ATH9K_BTCOEX_SUPPORT`, the hardware-reset and calibration helpers are real external functions. Without that option, most helpers compile to no-ops or conservative return values, allowing common ath9k code to call them unconditionally.

## State and Persistence Behavior
The header does not allocate state. It names transient driver states and packed on-wire/in-ring values. `MCI_GPM_RECYCLE()` mutates a consumed GPM entry by writing the reserved pattern into its payload word, so the macro is part of the ring state protocol and not a pure accessor. `MCI_2G_FLAGS_*` and `MCI_5G_FLAGS_*` encode the state transition between 2 GHz coexistence mode and 5 GHz/non-shared mode.

## Dependencies and Integration Points
The header depends on common kernel/ath9k bit macros such as `BIT()`, `MS()`, and the forward declarations visible through included ath9k headers. It is included by `mci.h`, `ar9003_mci.c`, AIC/calibration/MAC/eeprom code, and reset paths. Public prototypes are also referenced indirectly by WoW power-save handling and by eeprom transmit-power logic through `ar9003_mci_get_max_txpower()` when BT concurrent TX constrains maximum power.

## Risks
The enum `mci_state_type` is broader than the implementation in `ar9003_mci_state()`. New callers can assume a state ID is implemented because it is declared here, but unhandled cases silently return zero. GPM byte offsets are hard-coded and endian/layout sensitive because the implementation casts `u32 *` payloads to `u8 *`. Some no-op stubs have signatures that differ slightly from the enabled implementation, notably the disabled `ar9003_mci_reset()` stub returning `void` while the enabled prototype returns `int`; callers in compiled configurations must match what the preprocessor exposes.

## Test Signals
Compile coverage should include both `CONFIG_ATH9K_BTCOEX_SUPPORT=y` and disabled builds to verify prototypes/stubs remain compatible. Protocol-level tests should validate GPM type/opcode packing, recycle marker behavior, 2G/5G flag masks, and antenna architecture predicates. Runtime logs from `ar9003_mci.c` are the practical signal that the constants here match hardware and BT firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_mci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_paprd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_paprd.c

## Purpose
`ar9003_paprd.c` implements peak-to-average power ratio distortion correction for AR9003 transmit chains. It configures PAPRD training, chooses training power, forces TX gain for training frames, reads hardware channel-info bins, builds the PA predistortion curve, stores the curve in calibration data, and writes the final PAPRD table into PHY registers.

## Important APIs, Types, and Functions
Exported APIs are `ar9003_paprd_enable()`, `ar9003_paprd_populate_single_table()`, `ar9003_paprd_setup_gain_table()`, `ar9003_paprd_create_curve()`, `ar9003_paprd_init_table()`, `ar9003_paprd_is_done()`, and `ar9003_is_paprd_enabled()`. The main internal helpers are `ar9003_get_training_power_2g()`, `ar9003_get_training_power_5g()`, `ar9003_paprd_setup_single_table()`, `ar9003_paprd_get_gain_table()`, `ar9003_get_desired_gain()`, `ar9003_tx_force_gain()`, `create_pa_curve()`, and `ar9003_paprd_retrain_pa_in()`.

The file uses `ah->paprd_target_power`, `ah->paprd_training_power`, `ah->paprd_ratemask`, `ah->paprd_ratemask_ht40`, `ah->paprd_table_write_done`, `ah->paprd_gain_table_entries`, and `ah->paprd_gain_table_index`. Per-channel persistent calibration data is stored in `struct ath9k_hw_cal_data`, especially `pa_table[chain]` and `small_signal_gain[chain]`.

## Control Flow
PAPRD setup begins with `ar9003_paprd_init_table()`, which calls `ar9003_paprd_setup_single_table()` and then snapshots the TX gain table. Setup selects 2 GHz or 5 GHz training power from current transmit power registers, target power, eeprom-derived scale factors, channel width, and chip revision. It writes AM2AM/AM2PM/HT40 masks, configures per-chain single-table mode and adaptive correction fields, disables PAPRD while training, and programs trainer control registers with chip-specific loopback, gain, quick-drop, ADC desired size, correction length, sample count, and pre/post scale settings.

For each chain, the upper driver calls `ar9003_paprd_setup_gain_table()` before sending a training frame. That function computes desired gain from target power, OLPC gain delta, thermal/voltage correction, desired scale, and closed-loop gain modifier, finds the first TX gain table index that satisfies the desired gain, and writes the decomposed gain fields into forced-gain registers.

After a training frame completes, `ar9003_paprd_create_curve()` reads two banks of 48 channel-info words from hardware, invokes `create_pa_curve()` to derive PA input and angle correction values, optionally requests retraining through `ar9003_paprd_retrain_pa_in()`, clears the train-done bit, and returns `0`, `-2`, `-EINPROGRESS`, or `-ENOMEM`. Successful curves are activated by `ar9003_paprd_populate_single_table()`, which writes `PAPRD_TABLE_SZ` values to the per-chain PAPRD memory table, writes small-signal gain, and programs training power into PAPRD control registers. `ar9003_paprd_enable()` then enables correction for active TX chains unless eeprom sub-band bits disable it.

## State and Persistence Behavior
PAPRD results persist in the in-memory `caldata` for the channel and in hardware PAPRD memory/control registers after activation. `ah->paprd_table_write_done` prevents repeated eeprom txpower/PAPRD table programming until reset code clears it. Gain-table snapshots persist in `ath_hw` between setup and per-chain training. No filesystem or firmware persistence is performed.

## Dependencies and Integration Points
`link.c` owns the workqueue flow (`ath_paprd_calibrate()`): initialize table, allocate/send PAPRD frames, wait for completion from TX status, call `ar9003_paprd_is_done()`, call `ar9003_paprd_create_curve()`, retry if requested, then activate tables. `xmit.c` marks PAPRD training frames and completes the PAPRD completion. `ar9003_eeprom.c` computes PAPRD target power and rate masks and disables rates whose target delta exceeds the scale factor. Register definitions come from `ar9003_phy.h`.

## Risks
`create_pa_curve()` is numerically dense fixed-point code with many division points and scale shifts; it has explicit zero guards but remains sensitive to sparse or noisy training bins. `ar9003_paprd_setup_gain_table()` does not clamp `gain_index` after scanning the gain table, so an unexpected desired gain above all entries risks indexing past the cached table in `ar9003_tx_force_gain()`. Some chip-specific quick-drop/capdiv adjustment paths can return `-EINPROGRESS` indefinitely if hardware measurements sit at the boundary. A source comment questions whether the B2 training-power field is correct, marking a maintenance risk.

## Test Signals
Strong signals are successful `ath_paprd_calibrate()` completion, `PAPRD_TRAIN_DONE` with acceptable AGC2 power, no repeated `-EINPROGRESS` loops, populated nonzero `caldata->pa_table` and `small_signal_gain`, correct per-chain PAPRD memory writes, and stable throughput/EVM improvements without transmit power regressions. Regression tests should cover 2 GHz/5 GHz, HT20/HT40, one/two/three-chain masks, AR9330/9485/9462/9565 revision branches, and eeprom sub-band PAPRD disable bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_paprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_phy.c

## Purpose
`ar9003_phy.c` is the AR9003 PHY operation implementation for ath9k. It provides channel synthesis, PLL selection, INI programming, baseband activation, spur mitigation, ANI control, noise-floor reads, radar/DFS setup, antenna diversity, fast channel change, spectral scan, TX99 support, transmit-power rate table initialization, operation-table attachment, and baseband watchdog handling.

## Important APIs, Types, and Functions
The primary exported/externally used entry point is `ar9003_hw_attach_phy_ops()`, which fills `ath_hw_private_ops` and `ath_hw_ops`. Other non-static functions are `ar9003_hw_set_chain_masks()`, `ar9003_hw_init_rate_txpower()`, `ar9003_hw_bb_watchdog_check()`, `ar9003_hw_bb_watchdog_config()`, `ar9003_hw_bb_watchdog_read()`, `ar9003_hw_bb_watchdog_dbg_info()`, and `ar9003_hw_disable_phy_restart()`.

Important static operation implementations include `ar9003_hw_set_channel()`, spur mitigation helpers for CCK/OFDM, `ar9003_hw_compute_pll_control*()`, `ar9003_hw_set_channel_regs()`, `ar9003_hw_init_bb()`, `ar9003_hw_process_ini()`, `ar9003_hw_set_rfmode()`, `ar9003_hw_set_delta_slope()`, `ar9003_hw_rfbus_req()`, `ar9003_hw_rfbus_done()`, `ar9003_hw_ani_control()`, `ar9003_hw_do_getnf()`, `ar9003_hw_ani_cache_ini_regs()`, `ar9003_hw_set_radar_params()`, antenna-diversity helpers, `ar9003_hw_fast_chan_change()`, spectral scan helpers, and TX99 helpers.

## Control Flow
Device attach calls `ar9003_hw_attach_phy_ops()`. That stores function pointers for channel programming, INI loading, baseband activation, RF bus access, ANI, noise floor, radar, fast channel change, spectral scan, antenna diversity, and TX99; it also initializes noise-floor limits, default radar config, and the CCA register list.

On reset/channel setup, the core uses `process_ini`, `rf_set_freq`, `set_channel_regs`, `init_bb`, and related callbacks. `ar9003_hw_process_ini()` chooses a modal column from band and HT width, programs split SOC/MAC/BB/radio arrays, applies chip-specific post arrays, applies RX/TX gain arrays, handles fast-clock and Japan channel 2484 special cases, stores `ah->modes_index`, runs `ar9003_hw_override_ini()`, sets channel registers and chain masks, and reapplies transmit power. `ar9003_hw_set_channel()` computes synthesizer channel select values for 2 GHz/5 GHz and 25/40 MHz reference clocks, writes synth registers, toggles load, and updates `ah->curchan`.

ANI control updates OFDM weak signal detection, first-step level, spur immunity, and MRC CCK according to `ath9k_ani_cmd` values while caching default INI values in `ah->ani.iniDef`. Spur mitigation reads eeprom spur channels and configures CCK/OFDM masks if a spur lies within the active channel range. Radar configuration writes FIR/RSSI/pulse thresholds and optional DFS INI. Spectral scan config writes count/period/FFT-period and handles the hardware convention that count zero means endless scans.

The baseband watchdog path saves hardware status in interrupt context, decides whether a full chip reset is needed for known signatures, can patch DFS FIR power for one signature, logs decoded state-machine fields in bottom-half context, and disables PHY restart after the unsupported-rate RX state-machine hang signature.

## State and Persistence Behavior
State is held in `struct ath_hw`: current channel, `modes_index`, chain masks, enabled calibration bits, ANI state/defaults, noise-floor limits and register list, radar config, watchdog last status/timeout/hang flag, and per-rate `tx_power` arrays. Hardware state is mostly register programming. No persistent storage is written.

## Dependencies and Integration Points
The file depends on `ar9003_phy.h` for register maps, `ar9003_eeprom.h` for spur/eeprom helpers, common hw ops/macros, and revision predicates such as `AR_SREV_9462()`/`AR_SREV_9565()`. `ar9003_hw.c` calls `ar9003_hw_attach_phy_ops()` during hardware attach and configures watchdog timeout defaults. `ar9003_mac.c` reads watchdog status from ISR. Calibration, reset, spectral scan, DFS, tx99, and antenna-combining code call through the operation tables populated here. `ar9003_rtt.c` uses the `rfbus_req`/`rfbus_done` operations to safely restore radio retention tables.

## Risks
This file has high hardware-sequencing risk: wrong modal column, revision predicate, clock mode, or register delay can break channel bring-up. Fast channel change reloads only selected post arrays, so it relies on `modes_index` tracking being correct. Spur mitigation and spectral scan share radar/PHY registers and can interact with DFS behavior. ANI writes are range-checked for levels, but their effects are sensitive to cached INI defaults. Watchdog signature handling is intentionally heuristic and unknown signatures force full reset. `ar9003_hw_set_chain_masks()` has special handling for chainmask `5` and APM three-chain TX, so chainmask tests are important.

## Test Signals
Reset/channel-change tests should verify successful synth programming, baseband activation, correct `modes_index`, and no PHY hangs across 2 GHz/5 GHz/HT20/HT40/half/quarter-rate channels. ANI tests should confirm counter changes and register updates for each command. DFS/radar tests should check programmed thresholds and event behavior. Spectral scan tests should verify finite versus endless count behavior. Watchdog tests should inject or observe known signatures and confirm reset/no-reset decisions and debug output. TX power tests should verify CCK/OFDM/HT/STBC rate arrays from eeprom target powers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_phy.h

## Purpose
`ar9003_phy.h` is the AR9003 PHY register map and field-definition header. It gives the implementation files symbolic names for channel, MRC, AGC, synthesizer, per-chain, global, RTT, watchdog, PAPRD, BT coexistence, and 65 nm radio registers. It is foundational for `ar9003_phy.c`, `ar9003_paprd.c`, `ar9003_rtt.c`, MCI/AIC code, and calibration routines.

## Important APIs, Types, and Defines
This header exports macros rather than functions. Register regions include `AR_CHAN_BASE`, `AR_MRC_BASE`, `AR_AGC_BASE`, `AR_SM_BASE`, per-chain channel/AGC/SM bases, and `AR_GLB_BASE`. Dynamic macros such as `AR_PHY_TEST(_ah)`, `AR_PHY_CHAN_INFO_MEMORY(_ah)`, `AR_PHY_PAPRD_TRAINER_CNTL*(_ah)`, `AR_PHY_RTT_TABLE_SW_INTF_B(i)`, and `AR_PHY_65NM_RXRF_AGC(i)` encode chip-revision or chain-dependent offsets.

Major field groups cover spur mitigation (`AR_PHY_TIMING11_*`, pilot/channel/spur masks), ANI and signal detection (`AR_PHY_SFCORR*`, `AR_PHY_FIND_SIG*`, `AR_PHY_TIMING5_*`), radar/DFS (`AR_PHY_RADAR_*`), antenna diversity (`AR_PHY_MC_GAIN_CTRL`, `AR_ANT_DIV_*`), spectral scan (`AR_PHY_SPECTRAL_SCAN_*`), radio retention (`AR_PHY_RTT_*`), baseband watchdog (`AR_PHY_WATCHDOG_*`), PAPRD control/trainer/table fields, BT coexistence LNA-diversity fields, and manual peak-detector/radio AGC fields.

## Control Flow
There is no runtime control flow, but the macro layout directly shapes control flow in implementation files. Channel setup uses synth, mode, active, RX delay, chainmask, and delta-slope definitions. PAPRD setup/training uses the PAPRD control, trainer, status, memory-table, PA gain, TX power, thermal/voltage, forced-gain, and channel-info macros. RTT uses `AR_PHY_RTT_CTRL` and the software table-interface macros. Watchdog code decodes state-machine fields with the watchdog masks. BT antenna diversity and MCI observation use global and coexistence register definitions.

## State and Persistence Behavior
The header does not hold state. It defines the register addresses and bit masks used to create hardware state. Because many definitions are revision-dependent macros, the same source operation can write different offsets on AR9485, AR9561, AR9462, AR9565, and related chips. This means hardware state persistence across reset depends on the caller using the correct revision predicate and reprogramming all required fields.

## Dependencies and Integration Points
The header assumes access to revision predicates and bitfield helpers such as `AR_SREV_*`, `SM()`, and `MS()` from the ath9k hardware layer. It is included by PHY, PAPRD, RTT, MCI, calibration, eeprom, and AIC files. It bridges high-level driver operation tables to raw hardware registers and is also indirectly part of debug/test behavior because watchdog and spectral/radar field decoding depends on these masks.

## Risks
Register headers carry structural risk: a wrong address, mask, shift, or revision predicate can silently program the wrong hardware field. Several macros reference an `ah` identifier inside their expression rather than only their formal parameter, which requires callers to have the expected variable name in scope. Dynamic offsets must stay synchronized with silicon revisions. Duplicated or nearby definitions, such as RX delay and multiple per-chain TPC symbols, can be easy to misuse. PAPRD and RTT definitions are tightly coupled to table sizes and packed data fields in other headers.

## Test Signals
Compile coverage across supported chip revisions is important because macro expressions depend on revision predicates. Runtime signals include successful channel bring-up, correct per-chain register writes, valid PAPRD training status/table programming, working RTT restore, spectral scan completion, decoded watchdog fields, and functioning BT antenna diversity. Hardware register dumps around reset and calibration are the most direct validation that these definitions align with silicon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_rtt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_rtt.c

## Purpose
`ar9003_rtt.c` implements AR9003 radio retention table support for PCOEM builds. RTT stores selected radio calibration values per receive chain so they can be restored without rerunning the full calibration path. The file enables/disables RTT, reads and writes RTT table entries through the software table interface, captures table history into calibration data, clears it, and restores it during channel reset.

## Important APIs, Types, and Functions
The public functions are `ar9003_hw_rtt_enable()`, `ar9003_hw_rtt_disable()`, `ar9003_hw_rtt_set_mask()`, `ar9003_hw_rtt_force_restore()`, `ar9003_hw_rtt_load_hist()`, `ar9003_hw_rtt_fill_hist()`, `ar9003_hw_rtt_clear_hist()`, and `ar9003_hw_rtt_restore()`. Internal helpers are `ar9003_hw_rtt_load_hist_entry()`, `ar9003_hw_rtt_fill_hist_entry()`, and `ar9003_hw_patch_rtt()`.

The retained values live in `ah->caldata->rtt_table[AR9300_MAX_CHAINS][MAX_RTT_TABLE_ENTRY]`. The code also uses `ah->caldata->cal_flags`, especially `RTT_DONE` and `SW_PKDET_DONE`, and `ah->caldata->caldac[]` for peak-detector patching.

## Control Flow
`ar9003_hw_rtt_fill_hist()` iterates active RX chains, reads each of the six RTT entries through the software access register pair, patches entry 5 for chains 0/1 when software peak-detector calibration is present, logs the values, stores them in `caldata`, and sets `RTT_DONE`. `ar9003_hw_rtt_load_hist()` performs the reverse operation by writing stored values back into the hardware RTT table for active chains.

`ar9003_hw_rtt_restore()` is the main restore path. It first rejects missing `caldata`. If software peak-detector data exists, it writes chain 0/1 caldac overrides into 2 GHz or 5 GHz AGC fields and enables AGC override. It requires `RTT_DONE`, enables RTT, sets the restore mask to `0x30` with peak-detector data or `0x10` without it, requests the RF bus to stop baseband access, loads retained table entries, forces hardware restore, releases the RF bus, disables RTT, and returns whether restore completed.

## State and Persistence Behavior
RTT values persist in memory as part of per-channel calibration data. They are not written to disk or firmware. Hardware state is transient and explicitly enabled only around load/restore or calibration capture. `ar9003_hw_rtt_clear_hist()` writes zeros to all active-chain RTT entries and clears `RTT_DONE`, making future restore attempts fail until a new fill occurs.

## Dependencies and Integration Points
This file depends on `ar9003_phy.h` for RTT and 65 nm AGC register definitions and on `hw-ops.h` for RF bus operations exposed by PHY ops. `ar9003_calib.c` calls RTT restore before calibration, enables/clears RTT around calibration, fills history after successful calibration, and reloads history in some paths. The public declarations are gated by `CONFIG_ATH9K_PCOEM` in `ar9003_rtt.h`.

## Risks
The software table interface relies on short `udelay(1)` sequencing and `ath9k_hw_wait()` polling. `ar9003_hw_rtt_load_hist_entry()` silently returns on an access timeout, so a partial load can still be followed by forced restore. `ar9003_hw_rtt_fill_hist_entry()` returns `RTT_BAD_VALUE` on timeout and the caller stores it like a table value. Peak-detector patching only handles entry 5 and chains below 2, so hardware with more chains or different layout needs care. `ar9003_hw_rtt_restore()` calls `ath9k_hw_rfbus_done()` even on RF bus request failure, relying on the operation being harmless.

## Test Signals
Test signals include `RTT_DONE` being set after calibration, valid non-`RTT_BAD_VALUE` table entries, successful `ar9003_hw_rtt_force_restore()` waits, RF bus grant success, stable caldac override behavior on 2 GHz and 5 GHz, and no calibration regressions when `CONFIG_ATH9K_PCOEM` is disabled. Register traces should show RTT enable, mask write, table loads, force-restore bit self-clearing, and RTT disable in order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_rtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_rtt.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_rtt.h

## Purpose
`ar9003_rtt.h` declares the AR9003 radio retention table interface and provides no-op stubs when PCOEM support is not compiled. It lets calibration and reset code call RTT helpers without scattering preprocessor conditionals across the driver.

## Important APIs, Types, and Functions
When `CONFIG_ATH9K_PCOEM` is enabled, the header declares `ar9003_hw_rtt_enable()`, `ar9003_hw_rtt_disable()`, `ar9003_hw_rtt_set_mask()`, `ar9003_hw_rtt_force_restore()`, `ar9003_hw_rtt_load_hist()`, `ar9003_hw_rtt_fill_hist()`, `ar9003_hw_rtt_clear_hist()`, and `ar9003_hw_rtt_restore()`. When it is disabled, the same names are inline stubs: void functions do nothing and boolean functions return `false`.

## Control Flow
The header has no active control flow beyond compile-time selection. It creates two call patterns: PCOEM builds execute the implementation in `ar9003_rtt.c`, while non-PCOEM builds compile out RTT side effects. Callers can therefore try RTT restore opportunistically and fall back to normal calibration when the returned boolean is false.

## State and Persistence Behavior
No state is stored in the header. The enabled implementation stores retained calibration entries in `ath9k_hw_cal_data`; the disabled stubs leave all calibration state untouched. Because disabled `ar9003_hw_rtt_restore()` returns false, higher layers should not mark RTT restoration successful unless the implementation was present and hardware accepted it.

## Dependencies and Integration Points
The header depends on `struct ath_hw`, `struct ath9k_channel`, and `u32` definitions from the surrounding ath9k include graph. It is included by `ar9003_rtt.c` and calibration code. It also depends indirectly on `ar9003_phy.h` because the implementation uses RTT register macros there, though this header only publishes the function contract.

## Risks
Stubbed-out builds can hide dead code in the enabled implementation unless both configurations are compiled. Because the stub functions silently do nothing, callers must use return values where available and not assume side effects occurred. API changes must keep enabled prototypes and disabled stubs synchronized exactly.

## Test Signals
Build tests should cover both `CONFIG_ATH9K_PCOEM=y` and disabled configurations. Runtime tests in enabled builds should verify RTT restore can avoid unnecessary calibration, while disabled builds should continue through the normal calibration path with no unresolved symbols and no behavioral dependency on RTT state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_rtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_wow.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_wow.c

## Purpose
`ar9003_wow.c` implements Wake-on-Wireless-LAN support for AR9003 hardware. It programs user wake patterns, creates the hardware keep-alive frame, enables wake events such as magic packet/link change/beacon miss/user pattern, transitions the MAC/RTC/PCIe state into WoW sleep, reads wake reasons, clears wake events, and restores selected power/reset state on wake.

## Important APIs, Types, and Functions
Exported APIs are `ath9k_hw_wow_apply_pattern()`, `ath9k_hw_wow_wakeup()`, and `ath9k_hw_wow_enable()`. Internal helpers are `ath9k_hw_set_sta_powersave()`, `ath9k_hw_set_powermode_wow_sleep()`, `ath9k_wow_create_keep_alive_pattern()`, and `ath9k_hw_wow_set_arwr_reg()`.

The file uses `ah->wow.wow_event_mask`, `ah->wow.wow_event_mask2`, and `ah->wow.max_patterns` from `struct ath9k_hw_wow`; current MAC/BSSID from `ath_common`; current channel and chainmask from `ath_hw`; and WoW register definitions from `reg_wow.h`.

## Control Flow
`ath9k_hw_wow_apply_pattern()` validates the pattern index against hardware capacity, enables the pattern bit in legacy or extended pattern registers, writes fixed-size pattern and mask tables in 32-bit chunks, records the corresponding enabled wake-event bit in `wow_event_mask` or `wow_event_mask2`, writes the pattern length into one of four packed length registers, and returns `0` or `-ENOSPC`.

`ath9k_hw_wow_enable()` begins from the accumulated user-pattern mask, enables PCIe PME-related control bits, configures random backoff, AIFS/slot/keep-alive counts, beacon timeout, keep-alive timeout/delay, writes a generated keep-alive frame descriptor and data buffer, enables or disables link-change and beacon-miss event generation, enables magic packet matching when requested, enables pattern matching for packets under 256 bytes, programs host PM control for D1/D3 or AR9462 real D3, clears sequence-number preservation so hardware can transmit while asleep, applies a PCIe PHY low-power tweak, applies PCIe reset/POR wiring changes, keeps RTC awake for MCI, disables a PCU WoW bit, transitions to WoW sleep, and stores the final event mask.

`ath9k_hw_wow_wakeup()` reads legacy and extended WoW status registers, masks out events that were not enabled by the driver, maps hardware status bits to `AH_WOW_*` result flags, clears PME, clears all WoW events, restores RSSI threshold, restores PCIe power-save wiring, restarts TSF2 generation on affected chips if needed, clears the stored event masks, and returns the wake reason bitmap.

## State and Persistence Behavior
WoW state persists in hardware registers during sleep and in `ah->wow` event masks across the enable-to-wakeup interval. User patterns are stored in hardware pattern/mask tables. The keep-alive frame is generated from current station MAC and BSSID and stored in hardware WoW TX buffer registers. On wake, event masks are cleared in memory and event bits are cleared in hardware. No filesystem persistence is used.

## Dependencies and Integration Points
This file depends on `ath9k.h`, `reg.h`, `reg_wow.h`, and `hw-ops.h`. It integrates with MCI through `ath9k_hw_mci_is_enabled()` and `ar9003_mci_state(MCI_STATE_GET_WLAN_PS_STATE)`. In this source snapshot, that MCI state query is declared but not handled in `ar9003_mci_state()`, so the default zero return makes WoW treat WLAN PS as disabled and set `AR_STA_ID1_PWR_SAV`. It integrates with PCIe power management through `ath9k_hw_configpcipowersave()` and with gen timers through `ath9k_hw_gen_timer_start_tsf2()`.

## Risks
`ath9k_hw_wow_apply_pattern()` always copies `MAX_PATTERN_SIZE` and `MAX_PATTERN_MASK_SIZE` bytes from caller-provided buffers, so callers must provide fully sized buffers even when `pattern_len` is smaller. Endianness and alignment of `memcpy()` into `u32` pattern words matter. Wake status can include spurious hardware bits, so masking with stored event masks is essential. Power-state sequencing is revision-specific, especially AR9462 D3 handling and TSF2 disable/restart logic. The MCI PS-state query edge means any future implementation of `MCI_STATE_GET_WLAN_PS_STATE` may change WoW sleep behavior.

## Test Signals
Test signals include successful pattern programming for legacy and extended slots, correct length register fields, expected wake reasons for magic packet/user pattern/link change/beacon miss, no wake reason for masked spurious bits, successful RX DMA stop before sleep, correct PCIe PME assertion, keep-alive frame transmission at 1 Mbps CCK or 6 Mbps OFDM as appropriate, TSF2 restart on wake for affected revisions, and clean interaction with MCI-enabled devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_wow.c -->

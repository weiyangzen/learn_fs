# Research: subset-b-004801

Grouped research report for subset B work item `subset-b-004801`. Each section is source-tree aligned and wrapped for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_cmn.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_cmn.c

## Purpose
`phy_cmn.c` is the common Broadcom `brcmsmac` PHY implementation used between the higher MAC/shim layer and PHY-type-specific backends. It owns shared attach/detach, register and table access helpers, radio identification, public PHY HAL entry points, channel metadata, transmit-power target calculation, RSSI/noise sampling, watchdog calibration scheduling, and dispatch into NPHY or LCNPHY callbacks through `struct phy_func_ptr`.

The file is hardware-facing. Most operations read or write D11 core registers, PHY registers, radio registers, or firmware shared memory, with MAC suspend/resume around operations that cannot run while MAC hardware is active.

## Important APIs, Types, and Functions
- Register access:
  - `read_phy_reg()`, `write_phy_reg()`, `and_phy_reg()`, `or_phy_reg()`, `mod_phy_reg()` wrap D11 PHY register access and maintain the PCI write-flush counter `pi->phy_wreg`.
  - `read_radio_reg()`, `write_radio_reg()`, `and_radio_reg()`, `or_radio_reg()`, `xor_radio_reg()`, and `mod_radio_reg()` add PHY-type-specific radio read offsets before MMIO.
  - `wlc_phyreg_enter()` and `wlc_phyreg_exit()` use shim wake overrides so register access can safely run while ucode would otherwise sleep.
- Attach and lifecycle:
  - `wlc_phy_shared_attach()` allocates `struct shared_phy` and copies chip, board, SROM, timer, shim, and default RSSI state.
  - `wlc_phy_attach()` validates D11 band flags, discovers `phy_type`, `phy_rev`, `radioid`, `radiorev`, and `radiover`, initializes defaults, then calls `wlc_phy_attach_nphy()` or `wlc_phy_attach_lcnphy()`.
  - `wlc_phy_detach()` reference-counts shared dual-band instances, removes timers, calls type-specific detach, and frees the `brcms_phy`.
  - `wlc_set_phy_uninitted()` resets persistent per-PHY software state to sentinel values before initialization.
- Public HAL entry points:
  - Version/state: `wlc_phy_get_phyversion()`, `wlc_phy_get_encore()`, `wlc_phy_get_coreflags()`, `wlc_phy_hw_clk_state_upd()`, `wlc_phy_hw_state_upd()`, `wlc_phy_por_inform()`, `wlc_phy_initcal_enable()`.
  - Initialization and shutdown: `wlc_phy_init()`, `wlc_phy_cal_init()`, `wlc_phy_down()`.
  - Channel/radio: `wlc_phy_chanspec_set()`, `wlc_phy_chanspec_get()`, `wlc_phy_chanspec_radio_set()`, `wlc_phy_bw_state_set()`, `wlc_phy_clk_bwbits()`, `wlc_phy_chanspec_band_validch()`, `wlc_phy_channel2freq()`, `wlc_phy_switch_radio()`, `wlc_phy_anacore()`.
  - Transmit power: `wlc_phy_txpower_get()`, `wlc_phy_txpower_set()`, `wlc_phy_txpower_sromlimit()`, `wlc_phy_txpower_limit_set()`, `wlc_phy_txpower_recalc_target()`, `wlc_phy_txpower_update_shm()`, `wlc_phy_txpower_get_current()`, `wlc_phy_txpower_hw_ctrl_get()`.
  - Antenna/chains: `wlc_phy_ant_rxdiv_set()`, `wlc_phy_antsel_type_set()`, `wlc_phy_stf_chain_init()`, `wlc_phy_stf_chain_set()`, `wlc_phy_stf_chain_active_get()`.
  - Calibration/noise/RSSI: `wlc_phy_watchdog()`, `wlc_phy_cal_perical()`, `wlc_phy_noise_sample_intr()`, `wlc_phy_rssi_compute()`, `wlc_phy_compute_dB()`.
- Table and radio initialization helpers:
  - `wlc_phy_table_addr()`, `wlc_phy_table_data_write()`, `wlc_phy_write_table()`, and `wlc_phy_read_table()` implement indexed PHY table IO.
  - `wlc_phy_init_radio_regs_allbands()` and `wlc_phy_init_radio_regs()` write static radio tables, with band selection and NPHY workaround flushes.
  - `wlc_phy_do_dummy_tx()` creates a short template packet and drives D11 transmit state for calibration and analog settling.
- Static data:
  - `chan_info_all[]` maps supported 2.4 GHz, 5 GHz, and Japanese 4.9 GHz channels to MHz.
  - `ofdm_rate_lookup[]` maps OFDM power-order indices to Broadcom rate encodings.

## Control Flow
Attach starts with `wlc_phy_shared_attach()` allocating shared chip state. `wlc_phy_attach()` then checks whether the requested band is physically present, resets the core through the shim, reads `phyversion`, normalizes LCNXN as NPHY, validates the PHY type, powers analog core on long enough to read the radio ID, checks the radio against valid NPHY/LCNPHY IDs, powers the radio off, initializes common defaults, installs type-specific function pointers, reads SROM-type data through the backend, and publishes a read-only `brcms_phy_pub` copy.

Initialization is driven by `wlc_phy_init()`. It rejects reentrant init, records the target chanspec, verifies the MAC is disabled and fast clock is available, sets the not-associated hold bit when not scanning, powers analog/radio blocks, switches bandwidth if needed, dispatches `pi->pi_fptr.init`, clears POR state, optionally performs a dummy transmit workaround, updates SHM transmit-power state for non-NPHY, restores RX diversity, and clears `init_in_progress`.

Channel setting writes `M_CURCHANNEL` in shared memory with channel, 5 GHz, and 40 MHz bits, then calls the backend `chanset` callback. Band-valid-channel generation walks `chan_info_all[]`, honors `a_band_high_disable`, and sets bits in `struct brcms_chanvec`.

Transmit-power recalculation combines user targets, optional RF-port conversion, SROM board limits, regulatory limits, a fixed `pactrl` margin, a hard 1.5 dB subtraction, percentage scaling, minimum limits, and environment limits. It stores per-rate targets, global min/max, and offsets, then calls the backend `txpwrrecalc` callback so NPHY or LCNPHY can program hardware tables. Regulatory limit setting first maps `struct txpwr_limits` into the internal 101-rate table, including NPHY OFDM/MCS cross-conversion, then suspends MAC, recalculates, and resumes MAC.

Noise sampling can be interrupt-driven through `MCMD_BG_NOISE` and `wlc_phy_noise_sample_intr()`, or direct polling. NPHY direct sampling disables classifiers, collects IQ estimates, converts complex power to dB, and updates per-core windows. LCNPHY direct sampling enters/deafens receiver modes and calls `wlc_lcnphy_rx_signal_power()`. Completion flows through `wlc_phy_noise_cb()`, which updates monitor/external state and the moving window.

The watchdog increments `sh->now`, samples noise unless scan/RM/PLT is active, times out stale noise operations, optionally recalculates software transmit power, and skips calibration while scan/RM/PLT/association is active. NPHY watchdog calibration may run periodic calibration and PAPD recalibration. LCNPHY watchdog may run temperature-based power adjustment and full calibration unless held or disabled.

## State and Persistence
All state is runtime driver state. `struct shared_phy` persists while the device is attached and holds chip identity, board flags, timers, current `up/clk` state, antenna diversity, chain masks, and shared noise windows. `struct brcms_phy` persists per PHY and holds public PHY identity, backend function pointers, D11 core handle, chanspec, bandwidth, calibration state, power tables, SROM-derived limits, temperature thresholds, noise state, and PHY-type-specific substructures.

No disk persistence exists. SROM/SPROM data is read from bus-provided firmware/board data and cached into `brcms_phy` fields. Hardware state is reconstructed on init, channel switch, and calibration.

## Dependencies and Integration Points
- Linux kernel helpers: allocation, delays, bit operations, warnings, `container_of()`, and integer helpers.
- Broadcom bus/core headers: `brcm_hw_ids.h`, `chipcommon.h`, `aiutils.h`, `d11.h`, `phy_radio.h`, `phyreg_n.h`.
- Public/private PHY headers: `phy_hal.h`, `phy_int.h`, `phy_lcn.h`.
- Shim integration through `wlapi_*` functions for MAC suspend/resume, timers, shared memory, template RAM, bandwidth, MHF bits, ucode wake overrides, and core reset.
- NPHY integration through many callbacks declared in `phy_int.h`, including NPHY attach/init/channel, RSSI, PAPD, classifier, IQ estimation, TX power, and radio switch helpers.
- LCNPHY integration through attach/init/channel/TSSI/temperature/RX-power helpers implemented in `phy_lcn.c`.

## Risks and Edge Cases
- `wlc_phy_init()` returns early on several warnings without clearing `pi->init_in_progress`; a failed init precondition can leave later init attempts ignored.
- Register access is order- and core-revision-sensitive. Wrong read offsets or missed flushes can read stale radio data or overrun PCI write posting assumptions.
- `wlc_phy_txpower_sromlimit()` uses the index into `chan_info_all[]` for 5 GHz board power arrays; if a channel is not found, `i` reaches `ARRAY_SIZE(chan_info_all)` and still indexes `pi->hwtxpwr[i]` when `hwtxpwr` is non-NULL.
- `wlc_phy_txpower_reg_limit_calc()` only fills extended NPHY groups inside `ISNPHY()`. LCNPHY later maps a subset; unsupported rate slots may retain old values.
- Noise and calibration routines depend on hold bits. Missed `PHY_HOLD_*` state can calibrate during scan, association, or PLT flows and perturb radio behavior.
- LCNPHY RSSI computation indexes `lcnphy_gain_index_offset_for_pkt_rssi[gidx]` from RX status bits without an explicit bounds check, relying on hardware to produce valid gain indices.
- `wlc_phy_cal_txpower_recalc_sw()` is currently a stub returning false, so any expected common software power recalculation is absent.
- `wlc_phy_ldpc_override_set()` is a stub. Callers should not assume LDPC hardware state changes.

## Test Signals
- Build with NPHY and LCNPHY enabled and with representative D11 core revisions to cover alternate register paths.
- Attach tests should cover invalid band flags, invalid radio IDs, dual-band shared-PHY reference counting, LCN attach, NPHY attach, and timer allocation failure.
- Initialization tests should observe MAC-disabled precondition handling, fast-clock availability, bandwidth switch, backend callback invocation, dummy TX on D11 rev 11/12, and RX diversity restoration.
- Channel tests should validate SHM `M_CURCHANNEL`, channel-to-frequency mappings, 2G/5G valid-channel bitsets, channel 14 behavior, and disabled high 5 GHz channels.
- TX power tests should exercise user limits, regulatory limits, SROM limits, percentage scaling, LCN MCS offsets, NPHY OFDM/MCS conversions, and SHM update when hardware power control is on/off.
- Noise/RSSI tests should include interrupt-driven background noise, polling paths, fixed-noise mode, stale `phynoise_state` timeout, LCN gain index RSSI correction, and NPHY RSSI compute.
- Watchdog tests should toggle scan/RM/PLT/association/disable flags and verify calibration is run or skipped as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_cmn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_hal.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_hal.h

## Purpose
`phy_hal.h` is the public PHY hardware-abstraction contract exported from the Broadcom PHY layer to higher `brcmsmac` driver layers. It defines radio ID constants, calibration and hold/mute reason constants, transmit-power data structures, channel-vector representation, shared attach parameters, and the callable PHY API used by MAC, channel, regulatory, scan, power-management, and statistics code.

The header intentionally hides `struct brcms_phy` internals. Higher layers interact through `struct shared_phy`, `struct brcms_phy_pub`, and opaque `phy_shim_info`/D11 handles.

## Important APIs, Types, and Functions
- Radio identity macros:
  - `IDCODE_*` masks/shifts decode radio IDCODE fields.
  - `NORADIO_ID`, `BCM2055_ID`, `BCM2056_ID`, `BCM2057_ID`, and `BCM2064_ID` identify supported radio families and known A0 IDCODEs.
- Calibration and hold constants:
  - `PHY_PERICAL_*` reason constants identify driver-up, watchdog, PHY init, BSS join/start/up, channel, and full calibration events.
  - `PHY_PERICAL_DISABLE`, `PHY_PERICAL_SPHASE`, `PHY_PERICAL_MPHASE`, and `PHY_PERICAL_MANUAL` configure periodic calibration modes.
  - `PHY_HOLD_FOR_*` flags suppress or defer measurements during association, scan, RM, PLT, mute, or not-associated conditions.
  - `PHY_MUTE_FOR_PREISM` and `PHY_MUTE_ALL` describe mute update contexts.
- Power and rate constants:
  - `BRCMS_TXPWR_DB_FACTOR` defines quarter-dBm units.
  - `BRCMS_TXPWR_MAX` is the high sentinel target/limit value.
  - `BRCMS_NUM_RATES_*` define CCK, OFDM, and MCS group sizes.
  - `PHY_NOISE_FIXED_VAL*` are fallback noise floors.
- Public data types:
  - `struct txpwr_limits` carries regulatory limits by CCK, OFDM, 20/40 MHz OFDM, SISO/CDD/STBC/MIMO MCS, and MCS32 groups.
  - `struct tx_power` is the reporting structure for current target, user, regulatory, board, estimated output, antenna gain, flags, and max-power-per-core values.
  - `struct brcms_chanvec` is a bit vector for valid channel sets.
  - `struct shared_phy_params` packages chip, board, SROM, core revision, shim, and bus identity into `wlc_phy_shared_attach()`.
- Public lifecycle and state APIs:
  - `wlc_phy_shared_attach()`, `wlc_phy_attach()`, and `wlc_phy_detach()`.
  - `wlc_phy_get_phyversion()`, `wlc_phy_get_encore()`, `wlc_phy_get_coreflags()`.
  - `wlc_phy_hw_clk_state_upd()`, `wlc_phy_hw_state_upd()`, `wlc_phy_init()`, `wlc_phy_watchdog()`, `wlc_phy_down()`, `wlc_phy_cal_init()`.
- Channel, radio, and antenna APIs:
  - `wlc_phy_chanspec_set()`, `wlc_phy_chanspec_get()`, `wlc_phy_chanspec_radio_set()`, `wlc_phy_bw_state_set()`, `wlc_phy_clk_bwbits()`.
  - `wlc_phy_chanspec_ch14_widefilter_set()`, `wlc_phy_chanspec_band_validch()`.
  - `wlc_phy_switch_radio()`, `wlc_phy_anacore()`, `wlc_phy_ant_rxdiv_set()`, `wlc_phy_antsel_type_set()`.
  - `wlc_phy_stf_chain_init()`, `wlc_phy_stf_chain_set()`, `wlc_phy_stf_chain_active_get()`.
- Power and calibration APIs:
  - `wlc_phy_txpower_sromlimit()`, `wlc_phy_txpower_limit_set()`, `wlc_phy_txpower_get()`, `wlc_phy_txpower_set()`, `wlc_phy_txpower_target_set()`, `wlc_phy_txpower_hw_ctrl_get()`, `wlc_phy_txpower_get_current()`.
  - `wlc_phy_cal_perical()`, `wlc_phy_cal_papd_recal()`, `wlc_phy_initcal_enable()`.
  - `wlc_phy_get_tx_power_offset_by_mcs()` and `wlc_phy_get_tx_power_offset()` expose per-rate target offsets.
- Measurement and feature APIs:
  - `wlc_phy_rssi_compute()`, `wlc_phy_noise_sample_intr()`, `wlc_phy_bist_check_phy()`.
  - `wlc_phy_ofdm_rateset_war()`, `wlc_phy_bf_preempt_enable()`, `wlc_phy_machwcap_set()`, `wlc_phy_ldpc_override_set()`, `wlc_phy_get_ofdm_rate_lookup()`.

## Control Flow
Higher layers allocate shared PHY state with `wlc_phy_shared_attach()`, attach one or more bands with `wlc_phy_attach()`, then drive runtime state through explicit calls. Clock and up/down state are pushed into the PHY layer with `wlc_phy_hw_clk_state_upd()` and `wlc_phy_hw_state_upd()`. Channel changes flow through `wlc_phy_chanspec_set()`. Periodic work calls `wlc_phy_watchdog()`. Interrupt code reports completed noise samples through `wlc_phy_noise_sample_intr()`. Regulatory updates pass a populated `struct txpwr_limits` to `wlc_phy_txpower_limit_set()`, while user power requests call `wlc_phy_txpower_set()`.

The header does not implement control flow, but its function grouping shows the intended layering: MAC/shim code asks for PHY state changes through these APIs; `phy_cmn.c` handles common validation and dispatch; type-specific files such as `phy_lcn.c` program PHY/radio tables.

## State and Persistence Behavior
This header defines runtime state carriers but no storage. `struct shared_phy_params` is an attach-time input copied into `struct shared_phy`. `struct txpwr_limits` and `struct tx_power` are caller-owned exchange structures. `struct brcms_chanvec` is a caller-visible channel bitmap. No fields here imply disk persistence; power limits and PHY identity are reconstructed from board/SPROM data and hardware at attach/init time.

The API exposes mutable hardware/runtime state indirectly: channel, radio power, antenna diversity, chain masks, calibration mode, current TX power, and hold/mute flags.

## Dependencies and Integration Points
- Includes `brcmu_utils.h`, `brcmu_wifi.h`, and `phy_shim.h` for kernel/Broadcom helpers, channel/rate definitions, and the shim abstraction.
- Forward declares `struct d11regs` and `struct phy_shim_info`, and uses `struct bcma_device`, `struct wiphy`, and `struct d11rxhdr` without defining them locally.
- Consumed by higher `brcmsmac` MAC/channel/regulatory code and implemented mostly by `phy_cmn.c`, with type-specific backends reached through `phy_int.h` function pointers.

## Risks and Edge Cases
- `struct txpwr_limits` and `struct tx_power` layout must remain synchronized with constants such as `WL_TX_POWER_RATES` and internal `TXP_NUM_RATES`; `phy_cmn.c` has a compile-time check in one path.
- Units are quarter-dBm for most power values. Mixing dBm, qdBm, raw TSSI, and table indices is easy because several APIs use `u8`/`s8` without type distinction.
- Hold and mute flags are bit masks; callers must clear the same reason bits they set or measurement/calibration can remain suppressed.
- `wlc_phy_txpower_target_set()` and `wlc_phy_cal_papd_recal()` are declared here but not implemented in `phy_cmn.c`, so their definitions must be supplied elsewhere or configuration must avoid unresolved references.
- Some APIs return success unconditionally in current implementations, for example `wlc_phy_get_phyversion()`, so callers should not treat `bool` as proof of hardware liveness unless implementation changes.

## Test Signals
- Header/API build tests should include every translation unit that includes `phy_hal.h` to catch missing forward declarations and layout drift.
- Attach/init smoke tests should call the public lifecycle functions through normal driver bring-up.
- Regulatory and user-power tests should validate `struct txpwr_limits` to internal target mapping for CCK, OFDM, MCS, STBC, CDD, and MCS32 groups.
- Channel tests should validate `struct brcms_chanvec` bit population and `wlc_phy_chanspec_*` state transitions.
- Runtime tests should cover hold/mute updates, watchdog invocation, noise interrupt delivery, RSSI compute, antenna diversity, and chain-state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_int.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_int.h

## Purpose
`phy_int.h` is the private internal contract for the `brcmsmac` PHY subsystem. It defines common PHY constants, rate-index layouts, calibration states, noise/interference structures, shared and per-PHY state structures, backend dispatch callbacks, table/radio descriptor formats, register helper prototypes, and NPHY/LCNPHY internal function prototypes.

This header is the main bridge between `phy_cmn.c`, NPHY implementation files, LCNPHY implementation files, PHY tables, and radio-specific code. Unlike `phy_hal.h`, it exposes `struct brcms_phy` internals and is not intended for higher driver layers.

## Important APIs, Types, and Data
- Version and PHY selection:
  - `PHY_VERSION` records the Broadcom PHY package version tuple.
  - `LCNXN_BASEREV` maps LCNXN revisions into NPHY revision space.
  - `ISNPHY(pi)` and `ISLCNPHY(pi)` wrap `PHYTYPE_IS()` checks against `pi->pubpi.phy_type`.
- Numeric helpers and channel/rate layout:
  - `PHY_GET_RFATTN()`, `PHY_GET_PADMIX()`, `PHY_GET_RFGAINID()`, `PHY_SAT()`, `PHY_SHIFT_ROUND()`, and `PHY_HW_ROUND()` support calibration math.
  - `CHAN5G_FREQ()` and `CHAN2G_FREQ()` provide simple channel-to-frequency formulas.
  - `TXP_FIRST_*`, `TXP_LAST_*`, `TXP_MCS_32`, and `TXP_NUM_RATES` define the internal 101-slot transmit-power rate table.
  - Core constants define up to four PHY cores and per-core indices.
- Calibration/noise/interference constants:
  - `PHY_NOISE_*` constants define noise sample modes, windows, offsets, moving-average sizes, and ucode sample logs.
  - TSSI, TX gain, PAPD, power minimum, spur-avoidance, software timer, and periodic-calibration constants parameterize backend algorithms.
  - `MPHASE_CAL_STATE_*` enumerates multi-phase NPHY calibration.
  - `enum phy_cal_mode` defines generic calibration mode labels used by implementations.
- Hold-state macros:
  - `SCAN_INPROG_PHY()`, `PLT_INPROG_PHY()`, `ASSOC_INPROG_PHY()`, `SCAN_RM_IN_PROGRESS()`, `PHY_MUTED()`, and `PUB_NOT_ASSOC()` query `pi->measure_hold`.
- Core structures:
  - `struct brcms_phy_srom_fem` stores FEM-related SROM fields for TSSI slope, external PA gain, detector range, TR isolation, and antenna switch LUT selection.
  - `struct phytbl_info` describes PHY table IO: pointer, length, ID, offset, and width.
  - `struct shared_phy` stores device-shared chip identity, shim, timers, up/clock state, antenna diversity, chain masks, and shared noise/RSSI state.
  - `struct brcms_phy_pub` is the small public identity/state block exposed read-only to higher layers.
  - `struct phy_func_ptr` is the backend dispatch table for init, calinit, channel set, TX power recalc, long training, TX IQ/LO access, radio LOFT, carrier suppress, RX signal power, and detach.
  - `struct brcms_phy` is the large private per-PHY state object: public identity, shared pointer, backend union, D11 core, init flags, channel/bandwidth, SROM power data, regulatory/user/target power arrays, calibration caches, NPHY state, LCN state pointer, table scratch fields, temperature state, noise state, and wiphy pointer.
- Calibration cache and backend structures:
  - `struct txiqcal_cache`, `struct rssical_cache`, `struct nphy_pwrctrl`, `struct nphy_txgains`, `struct nphy_txpwrindex`, `struct nphy_iq_comp`, `struct lcnphy_cal_results`, and related structures store calibration coefficients and power-control state.
  - `struct radio_regs`, `struct radio_20xx_regs`, and `struct lcnphy_radio_regs` describe radio initialization tables.
- Internal prototypes:
  - Common register/table helpers implemented by `phy_cmn.c`.
  - Shared math helpers such as `wlc_phy_nbits()` and `wlc_phy_compute_dB()`.
  - NPHY attach/init/channel/calibration/RSSI/TX-power/radio helpers.
  - LCNPHY attach/init/channel/TX-power/TSSI/temperature/IQ/LO/tone/RX-power helpers.
- LCNPHY table/power constants:
  - `LCNPHY_TBL_ID_PAPDCOMPDELTATBL`, `LCNPHY_TX_POWER_TABLE_SIZE`, `LCNPHY_TBL_ID_TXPWRCTL`, and `LCNPHY_TX_PWR_CTRL_*` define LCN table IDs and power-control modes.

## Control Flow
The header itself does not execute, but it defines the subsystem control model. Common code allocates `struct brcms_phy`, sets public identity in `pubpi`, initializes common state arrays, and calls the backend attach routine. Backend attach routines allocate their private state, populate `pi->pi_fptr`, and read board data. Later public HAL calls in `phy_cmn.c` run common preconditions and dispatch to callbacks in `pi_fptr`.

For NPHY, multi-phase calibration state is tracked in `mphase_cal_phase_id`, `mphase_txcal_cmdidx`, `phycal_timer`, and calibration caches. For LCNPHY, the `u.pi_lcnphy` pointer references the separate `struct brcms_phy_lcnphy` declared in `phy_lcn.h`, while common fields such as `hwpwrctrl`, `temppwrctrl_capable`, `txpa_2g[]`, `tx_power_target[]`, and `tx_power_offset[]` remain in `struct brcms_phy`.

PHY table IO uses `struct phytbl_info`: caller fills the descriptor, type-specific wrappers choose table address/data registers, then common table functions iterate entries and write/read 8-, 16-, or 32-bit values.

## State and Persistence Behavior
`struct brcms_phy` and `struct shared_phy` are runtime-only state. They persist for the lifetime of a driver attach and are freed on detach. They cache hardware identity, board/SPROM values, regulatory limits, calibration results, temperature/noise windows, per-rate power targets, backend-specific calibration state, and current channel/radio settings. None of the state is persisted to disk; it is reconstructed from hardware, SROM, and static tables.

Several fields mirror hardware state and can become stale if register programming fails or if another path changes hardware directly. Important mirrored fields include `radio_chanspec`, `bw`, `hwpwrctrl`, `tx_power_target[]`, `tx_power_offset[]`, `lcnphy_current_index` in the LCN block, NPHY calibration channel fields, chain masks, and noise windows.

## Dependencies and Integration Points
- Includes `types.h`, `brcmu_utils.h`, and `brcmu_wifi.h`.
- Consumed by `phy_cmn.c`, `phy_lcn.c`, NPHY implementation files, PHY table files, and radio headers.
- Integrates with Linux/driver types including `struct bcma_device`, `struct wiphy`, `struct d11rxhdr`, `struct wlapi_timer`, and `struct ssb_sprom` through fields and function prototypes.
- Depends on Broadcom macros and constants from included Wi-Fi/utility headers and radio/PHY register headers, such as `PHYTYPE_IS`, `CHSPEC_*`, `BFL_*`, `WL_TX_POWER_*`, and D11 shared-memory offsets.

## Risks and Edge Cases
- `struct brcms_phy` is very large and mixes common, NPHY, legacy, and LCN-related fields. Field reuse across PHY types can introduce accidental coupling and stale state.
- Many macros evaluate arguments multiple times or perform shifts on signed values. Callers should avoid side effects and validate ranges before using helper macros.
- The internal rate table layout must match public `WL_TX_POWER_RATES` assumptions and firmware/shared-memory rate ordering.
- `struct phy_func_ptr` members are optional. Common code must null-check callbacks before dispatch; missing callbacks can silently make operations no-ops.
- `PHY_PERICAL_MPHASE_PENDING(pi)` depends only on `mphase_cal_phase_id`; incorrect reset/schedule logic can leave periodic calibration stuck pending.
- Some arrays have hardware-derived indices, such as gain index, core number, channel index, and rate index. Bounds validation is left mostly to implementation code.
- The header exposes many prototypes across files; changes to signatures or state fields have a wide blast radius across common, NPHY, and LCNPHY code.

## Test Signals
- Compile all PHY configurations to catch signature drift, missing declarations, and layout assumptions.
- Static analysis should focus on array indexing by hardware values, signed shifts in macros, and optional callback checks.
- Runtime attach tests should verify `pi_fptr` is correctly populated for NPHY and LCNPHY and that common calls dispatch to the expected backend.
- Calibration tests should observe state transitions in `mphase_cal_phase_id`, NPHY/LCN calibration result caches, and channel-specific calibration cache fields.
- Power tests should validate every `TXP_*` rate-group mapping, including MCS32 and SISO/CDD/STBC/MIMO boundaries.
- Noise and RSSI tests should validate per-core window indexing and moving-average wrap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_lcn.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_lcn.c

## Purpose
`phy_lcn.c` implements the LCNPHY backend for Broadcom `brcmsmac`, primarily BCM2064 radio/LCN PHY hardware. It provides LCN-specific table access, radio/channel tuning, baseband/radio initialization, SROM power parsing, transmit-power control, TSSI and temperature/voltage sensing, TX IQ/LO calibration, RX IQ calibration, tone generation, calibration scheduling, RX gain/power measurement, and backend callbacks installed into `struct phy_func_ptr`.

The file is almost entirely hardware-programming logic. It writes PHY tables, PHY registers, radio registers, chipcommon PLL/chip control registers, and D11 sample/template paths. It relies on common code in `phy_cmn.c` for attach dispatch, shared state, common register helpers, watchdog calls, and higher-layer API entry points.

## Important APIs, Types, and Functions
- Static constants and hardware tables:
  - PLL/VCO constants configure BCM2064 channel tuning.
  - LCN table IDs, TX power table offsets, power-control mode constants, noise/ACI constants, and sample-play table IDs define hardware layout.
  - `chan_info_2064_lcnphy[]` maps 2.4 GHz channels to BCM2064 radio tuning values.
  - `lcnphy_radio_regs_2064[]` is the static radio init table.
  - `LCNPHY_txdigfiltcoeffs_cck` and `LCNPHY_txdigfiltcoeffs_ofdm` provide digital filter coefficient sets.
  - Gain, RSSI offset, IQ calibration ladder, RF register save-list, and sample-tone tables drive calibration and measurement loops.
- Local types:
  - `struct lcnphy_txgains` packs GM, PGA, PAD, and DAC gain.
  - `struct lcnphy_iq_est`, `struct lcnphy_rx_iqcomp`, `struct lcnphy_spb_tone`, `struct lcnphy_unsign16_struct`, and `struct lcnphy_sfo_cfg` support calibration and channel tuning.
  - `enum lcnphy_cal_mode`, `enum lcnphy_tssi_mode`, and `enum lcnphy_papd_cal_type` classify calibration and TSSI modes.
- Table and math helpers:
  - `wlc_lcnphy_write_table()` and `wlc_lcnphy_read_table()` wrap common table IO with LCN table registers.
  - `wlc_lcnphy_common_read_table()` and `wlc_lcnphy_common_write_table()` build `struct phytbl_info` descriptors.
  - `wlc_lcnphy_qdiv_roundup()` and `wlc_lcnphy_calc_floor()` implement fixed-point/division helpers.
- Gain and RF override helpers:
  - `wlc_lcnphy_get_tx_gain()`, `wlc_lcnphy_set_tx_gain()`, `wlc_lcnphy_set_dac_gain()`, `wlc_lcnphy_set_tx_gain_override()`, `wlc_lcnphy_set_pa_gain()`.
  - `wlc_lcnphy_rx_gain_override_enable()`, `wlc_lcnphy_set_rx_gain_by_distribution()`, `wlc_lcnphy_set_rx_gain()`.
  - `wlc_lcnphy_set_trsw_override()` and `wlc_lcnphy_clear_trsw_override()` force transmit/receive switch state.
- Power-control and sensing:
  - `wlc_lcnphy_tssi_setup()` configures TSSI muxing, ADC timing, RF sequence table, and power-control tables.
  - `wlc_lcnphy_tx_pwr_update_npt()`, `wlc_lcnphy_txpower_reset_npt()`, `wlc_lcnphy_txpower_recalc_target()`, `wlc_lcnphy_set_tx_pwr_soft_ctrl()`, `wlc_lcnphy_tempcompensated_txpwrctrl()`, `wlc_lcnphy_set_tx_pwr_ctrl()`, and `wlc_phy_txpower_recalc_target_lcnphy()` manage hardware, software, and temperature-based TX power modes.
  - `wlc_lcnphy_tssi2dbm()`, `wlc_lcnphy_get_tssi()`, `wlc_lcnphy_tempsense()`, `wlc_lcnphy_tempsense_new()`, `wlc_lcnphy_tempsense_degree()`, and `wlc_lcnphy_vbatsense()` convert raw measurements to power/temperature/voltage values.
  - `wlc_lcnphy_vbat_temp_sense_setup()` temporarily reprograms RF/PHY state to run sensor measurements.
- Calibration:
  - `wlc_lcnphy_rx_iq_est()`, `wlc_lcnphy_calc_rx_iq_comp()`, `wlc_lcnphy_rx_iq_cal_gain()`, and `wlc_lcnphy_rx_iq_cal()` measure and compensate RX IQ imbalance.
  - `wlc_lcnphy_tx_iqlo_loopback()`, `wlc_lcnphy_iqcal_wait()`, `wlc_lcnphy_tx_iqlo_cal()`, `wlc_lcnphy_tx_iqlo_soft_cal_full()`, and `wlc_lcnphy_txpwrtbl_iqlo_cal()` calibrate TX IQ/LO and copy results into the TX power table.
  - `wlc_lcnphy_samp_cap()` and `wlc_lcnphy_a1()` implement sample-capture/search based soft calibration.
  - `wlc_lcnphy_periodic_cal()`, `wlc_lcnphy_glacial_timer_based_cal()`, and `wlc_lcnphy_calib_modes()` orchestrate full, watchdog, PHY-init, and temperature-based calibration.
- Tone and transmit path:
  - `wlc_lcnphy_start_tx_tone()` generates a CORDIC tone into sample-play tables and starts sample playback.
  - `wlc_lcnphy_stop_tx_tone()` stops playback, restores spur mode, powers TX down, and exits deaf mode.
  - `wlc_lcnphy_tx_pu()` powers TX path up/down through RF override registers.
  - `wlc_lcnphy_crsuprs()` configures carrier suppression mode.
- Initialization and channel control:
  - `wlc_lcnphy_set_chanspec_tweaks()` configures channel-specific PLL/spur/filter tweaks.
  - `wlc_lcnphy_radio_2064_channel_tune_4313()` programs BCM2064 PLL/radio for a 2.4 GHz channel and runs VCO calibration.
  - `wlc_lcnphy_load_tx_iir_filter()`, `wlc_lcnphy_load_tx_gain_table()`, `wlc_lcnphy_load_rfpower()`, `wlc_lcnphy_tbl_init()`, `wlc_lcnphy_radio_init()`, `wlc_lcnphy_baseband_init()`, and revision-specific init helpers load static tables and tweak hardware.
  - `wlc_phy_init_lcnphy()` is the backend init callback.
  - `wlc_phy_chanspec_set_lcnphy()` is the backend channel callback.
  - `wlc_phy_attach_lcnphy()` allocates LCN state, sets capabilities, installs function pointers, and reads SROM.
  - `wlc_phy_detach_lcnphy()` frees LCN state.
- RX power:
  - `wlc_lcnphy_get_receive_power()` searches or applies an RX gain index and measures digital power.
  - `wlc_lcnphy_rx_signal_power()` converts measured power, gain table values, offsets, frequency correction, and temperature correction into input power dB.

## Control Flow
LCN attach occurs from `wlc_phy_attach()` in common code. `wlc_phy_attach_lcnphy()` allocates `struct brcms_phy_lcnphy`, enables hardware power control when the board has a PA, records the ALP clock, installs LCN callbacks, reads TX power/SROM data with `wlc_phy_txpwr_srom_read_lcnphy()`, and selects TSSI-based versus temperature-based power control for revision 1 depending on SROM `tempsense_option`.

LCN init starts in `wlc_phy_init_lcnphy()`. It initializes calibration counters, toggles AFE clocks, writes base timing registers, loads PHY tables, initializes baseband, initializes the BCM2064 radio, initializes TX power control for 2.4 GHz, applies the current chanspec, writes chipcommon control settings, optionally forces a fixed TX power index for FEM plus temperature control, snapshots AGC temperature-related values, triggers temperature adjustment, enables TX power control, sets default noise sample count, and runs PHY-init calibration.

Channel changes flow through `wlc_phy_chanspec_set_lcnphy()`. The function records the chanspec in common state, applies PLL/spur/channel tweaks, tunes the BCM2064 radio from `chan_info_2064_lcnphy[]`, delays for settling, toggles AFE powerdown, writes SFO config values indexed by channel, loads channel-14 or normal CCK filters plus FEM/non-FEM OFDM filters, tweaks RF override bits, and reruns TSSI setup when TSSI power control is supported.

Transmit-power control has three effective paths. TSSI hardware control programs the TX power table from SROM PA coefficients, estimates idle TSSI, writes target power, and enables `LCNPHY_TX_PWR_CTRL_HW`. Temperature-based control maps requests to `LCNPHY_TX_PWR_CTRL_TEMPBASED`, periodically recomputes a gain index from board-measured power and temperature slope, and writes the soft-control index register. Manual/off control disables hardware control, loads gain/IQ/LO/table values for a selected power index, and enables TX gain override.

Full periodic calibration suspends MAC when needed, enters deaf mode, runs TX power table IQ/LO calibration, runs RX IQ calibration, refreshes TSSI-to-dBm tables if hardware control is enabled, restores the previous TX power index and control mode, exits deaf mode, and resumes MAC. Watchdog calibration uses temperature delta/counter thresholds in temperature-based mode; otherwise common watchdog forces periodic modes through `wlc_lcnphy_calib_modes()`.

RX signal power measurement either scans gain indices until measured digital power crosses a threshold or measures at a caller-provided index. The result is converted from measured power to log-scaled dB, adjusted by gain mismatch, input-power offset, gain-index RSSI offset table, frequency correction, and last-sensed temperature, then RX gain override is disabled.

## State and Persistence Behavior
Runtime LCN-specific state lives in `struct brcms_phy_lcnphy` and is reachable as `pi->u.pi_lcnphy`. Important fields written here include current TX power index, TX power override index, calibration channel/counter/temperature, raw temperature and SROM calibration data, TSSI snapshot counters, RSSI/TSSI calibration parameters, MCS power offsets, gain-table offsets, last sensed temperature, IQ/LO calibration results, noise sample count, and saved user targets.

Common `struct brcms_phy` fields are also central: `hwpwrctrl`, `hwpwrctrl_capable`, `temppwrctrl_capable`, `txpa_2g[]`, `tx_srom_max_rate_2g[]`, `tx_power_min`, `tx_power_offset[]`, `tx_power_target[]`, `phy_lastcal`, `phy_forcecal`, `radio_chanspec`, `xtalfreq`, `phy_tx_tone_freq`, and board flags.

No persistent files are written. Board/SPROM values are read once at attach and cached. Calibration results persist only for the driver lifetime and are reloaded into hardware tables as needed.

## Dependencies and Integration Points
- Includes Linux delay, kernel, and CORDIC helpers.
- Uses Broadcom PMU/chipcommon APIs for PLL, chip control, and ALP clock.
- Uses D11 core registers for sample capture, template/sample-play, MAC control, and PHY status.
- Depends on common PHY APIs and structures from `phy_hal.h`, `phy_lcn.h`, `phy_int.h` through included paths, plus radio constants from `phy_radio.h`.
- Consumes static LCN PHY tables from `phytbl_lcn.h` and fixed-point math from `phy_qmath.h`.
- Calls common functions from `phy_cmn.c`: register/table helpers, `wlc_phy_nbits()`, `wlc_phy_channel2freq()`, `wlc_phy_do_dummy_tx()`, `wlc_phy_chanspec_set()`, `wlc_phy_chanspec_radio_set()`, and `wlc_phy_txpower_recalc_target()`.
- Exposes LCN callbacks used by `phy_cmn.c` through `pi->pi_fptr`.

## Risks and Edge Cases
- `wlc_phy_chanspec_set_lcnphy()` indexes `lcnphy_sfo_cfg[channel - 1]` without validating the channel. The table has 14 entries, so non-2.4 GHz or invalid channels would be unsafe.
- Several calibration routines allocate with `GFP_ATOMIC` and silently return on failure, leaving older calibration state active.
- Many save/restore blocks touch dozens of RF/PHY registers. Any early return before cleanup risks leaving override, deaf, loopback, or TX power control state enabled.
- `wlc_lcnphy_rx_iq_cal()` reads `RFOverrideVal0_old` but writes it back to both `0x44c` and `0x44d`; the apparent missing save for `RFOverride0_old` may restore an incorrect override register.
- `wlc_lcnphy_tx_iqlo_loopback_cleanup()` uses `and_phy_reg(pi, 0x44c, 0x0 >> 11)`, which evaluates to zero and clears the entire register rather than clearing selected bits.
- `wlc_lcnphy_start_tx_tone()` fills `data_buf[64]` with `num_samps` derived from frequency and bandwidth. The current frequencies appear bounded, but arbitrary callers could exceed the fixed buffer if a tone frequency produces more than 64 samples.
- `wlc_lcnphy_get_receive_power()` decrements `gain_index` after the search loop. If no threshold is crossed until after the max index, it can leave an out-of-range value for later `lcnphy_gain_table[gain_index]`.
- Temperature and voltage sensing temporarily disable TX power control and force high power indices; incorrect suspend detection or restore can perturb live traffic.
- The code contains empty or stub-like routines such as `wlc_lcnphy_temp_adj()` and `wlc_phy_cal_init_lcnphy()`, so some declared calibration phases intentionally do no work.

## Test Signals
- Attach/init tests should cover board flags with/without `BFL_NOPA`, `BFL_FEM`, `BFL_FEM_BT`, `BFL_EXTLNA`, revision 0/1/2 paths, and SROM fields for temperature/TSSI control.
- Channel tests should cover channels 1-14, especially channel 14 filter selection and PLL/spur mode differences between low/mid channels.
- TX power tests should exercise TSSI hardware control, temperature-based control, power-control-off/manual index mode, user/regulatory target changes, MCS20 offsets, and FEM/non-FEM gain tables.
- Calibration tests should observe TX IQ/LO table updates, RX IQ coefficient updates, save/restore of power-control mode, deaf mode, tone start/stop, and MAC suspend/resume.
- Sensor tests should verify `wlc_lcnphy_tempsense*()` and `wlc_lcnphy_vbatsense()` with `mode` 0 and 1, including restoration of radio and PHY registers.
- RX power tests should validate gain-index search boundaries, input-power calculation, frequency correction, and temperature correction.
- Fault-injection tests should simulate IQ estimate timeout, failed allocations, invalid channels, MAC active/inactive transitions, and hardware calibration-done timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_lcn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_lcn.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_lcn.h

## Purpose
`phy_lcn.h` defines `struct brcms_phy_lcnphy`, the LCNPHY-specific private state block embedded by pointer in `struct brcms_phy`. It stores SROM-derived calibration inputs, LCN runtime calibration state, transmit-power-control state, RSSI/TSSI parameters, gain/table offsets, PAPD/IQ/LO calibration results, channel and spur state, noise settings, and saved user target values.

The header is data-only: it has no functions and exists so common/private PHY code can reference LCN state without exposing it through the public HAL.

## Important APIs, Types, and Fields
- Main type:
  - `struct brcms_phy_lcnphy` is allocated by `wlc_phy_attach_lcnphy()` and freed by `wlc_phy_detach_lcnphy()`.
- Calibration scheduling fields:
  - `lcnphy_full_cal_channel`, `lcnphy_cal_counter`, `lcnphy_cal_temper`, and `lcnphy_recal` track when full or glacial calibration should rerun.
  - `lcnphy_cal_results` stores `struct lcnphy_cal_results` from `phy_int.h`, including TX IQ/LO coefficients, PAPD table parameters, and RX IQ coefficients.
- Board/SROM power fields:
  - `lcnphy_mcs20_po`, `lcnphy_tr_isolation_*`, `lcnphy_rx_power_offset`, `lcnphy_pa0b0/1/2`, `lcnphy_rawtempsense`, `lcnphy_measPower`, `lcnphy_tempsense_slope`, `lcnphy_freqoffset_corr`, `lcnphy_tempsense_option`, and `lcnphy_tempcorrx`.
  - `lcnphy_54_48_36_24mbps_backoff`, `lcnphy_11n_backoff`, `lcnphy_lowerofdm`, `lcnphy_cck`, and `lcnphy_tx_power_offset[]` support per-rate power behavior.
- RSSI/TSSI and gain fields:
  - `lcnphy_rssi_vf`, `lcnphy_rssi_vc`, `lcnphy_rssi_gs`, plus low/high-temperature copies.
  - `lcnphy_tssi_val`, `lcnphy_tssi_tx_cnt`, `lcnphy_tssi_idx`, `lcnphy_tssi_npt`.
  - `lcnphy_gain_idx_*`, `lcnphy_ofdmgainidxtableoffset`, `lcnphy_dsssgainidxtableoffset`, `lcnphy_tr_R_gain_val`, `lcnphy_tr_T_gain_val`, `lcnphy_input_pwr_offset_db`, `lcnphy_Med_Low_Gain_db`, `lcnphy_Very_Low_Gain_db`, and `lcnphy_pkteng_rssi_slope`.
- Runtime TX/radio state:
  - `lcnphy_target_tx_freq`, `lcnphy_tx_power_idx_override`, `lcnphy_current_index`, `lcnphy_noise_samples`.
  - `lcnphy_spurmod`, `lcnphy_bandedge_corr`, `lcnphy_iqcal_swp_dis`, `lcnphy_hw_iqcal_en`.
  - PAPD/PSAT/LO fields such as `lcnphy_papdRxGnIdx`, `lcnphy_papd_rxGnCtrl_init`, `lcnphy_final_papd_cal_idx`, `lcnphy_psat_*`, `lcnphy_logen_*`, and `lcnphy_local_*`.
- Saved/auxiliary state:
  - `lcnphy_saved_tx_user_target[TXP_NUM_RATES]`, `lcnphy_volt_*`, `lcnphy_extstxctrl*`, `lcnphy_cck_dig_filt_type`, `lcnphy_ofdm_dig_filt_type`, `lcnphy_aci_stat`, and `lcnphy_aci_start_time`.

## Control Flow
The structure is populated in phases. Attach allocates and zeroes it, then `wlc_phy_txpwr_srom_read_lcnphy()` copies SPROM values into SROM-related fields. Initialization and channel setup update bandedge, spur, filter, AGC, and current-index fields. Power-control setup and recalculation update TSSI counters, current TX power index, and temperature-based compensation fields. Calibration routines write `lcnphy_cal_results` and update calibration counters/temperature snapshots. RX power routines use `lcnphy_noise_samples` and stored gain offsets.

The common `struct brcms_phy` owns the pointer and selects this block only when `ISLCNPHY(pi)` is true.

## State and Persistence Behavior
All fields are runtime cache/state for one attached PHY. Values originate from zeroed allocation, SPROM, static table reads, hardware measurements, and calibration results. They are not persisted across detach, reset, driver reload, or reboot. Some values mirror hardware registers or table contents and need refresh after full hardware reinitialization.

## Dependencies and Integration Points
- Includes `types.h`.
- Uses `TXP_NUM_RATES` and `struct lcnphy_cal_results`, which are declared in `phy_int.h`; the include order in C files must provide those definitions before this header is used.
- Allocated, populated, and consumed by `phy_lcn.c`; referenced by common code in `phy_cmn.c` for LCN RSSI packet correction and by any other internal PHY code that dereferences `pi->u.pi_lcnphy`.
- Tied to SPROM fields exposed through the bus and to LCN table/register definitions in `phy_lcn.c` and `phytbl_lcn.h`.

## Risks and Edge Cases
- This header relies on external definitions without including `phy_int.h`, so incorrect include order would break compilation.
- Many fields are narrow `u8`/`s8` caches for hardware-derived values. Overflow or sign conversion mistakes can affect power and RSSI calculations.
- Several fields appear to support partially implemented PAPD/ACI/PSAT paths; stale or unused state can be misleading during maintenance.
- Because the structure is zero-initialized, code must distinguish a legitimate zero calibration value from an uninitialized one. Some fields have explicit validity flags, such as `txiqlocal_bestcoeffs_valid`, but many do not.
- `lcnphy_saved_tx_user_target[]` duplicates common `tx_user_target[]`; restoring from the wrong copy could regress user power settings.

## Test Signals
- Compile tests should include all C files that include `phy_lcn.h` to verify include-order assumptions.
- Attach/init tests should check that SPROM values populate the expected fields and that defaults such as `lcnphy_cck_dig_filt_type = -1` are set by implementation code.
- Calibration tests should inspect `lcnphy_cal_results` after TX IQ/LO and RX IQ calibration.
- Power-control tests should track `lcnphy_current_index`, `lcnphy_tx_power_idx_override`, `lcnphy_tssi_idx`, and `lcnphy_tssi_npt` across mode transitions.
- RSSI/noise tests should verify `lcnphy_noise_samples`, RSSI slope/offset fields, and gain-table offset fields after init and measurement paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_lcn.h -->

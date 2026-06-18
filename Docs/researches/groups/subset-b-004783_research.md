# subset-b-004783 research group

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_g.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_g.c

## Purpose

`phy_g.c` implements the Broadcom b43 IEEE 802.11g PHY operation backend. It owns G-PHY allocation, reset-time structure preparation, baseband/radio initialization, 2050 radio calibration, channel switching, software RF kill, antenna diversity, adjacent-channel interference mitigation, TSSI to dBm conversion, software TX-power recalculation, and periodic G-PHY maintenance hooks. It is selected through `b43_phyops_g` and is the procedural counterpart to the register/state definitions in `phy_g.h`.

The file is highly hardware-specific. Most behavior is direct programming of PHY, radio, shared-memory, host-flag, and OFDM/G-PHY table registers through b43 core accessors. The source also keeps reverse-engineered workarounds for old 4306/2050 combinations, power-control quirks, PPC machine-check avoidance, and Japan channel 14 handling.

## Important APIs, Types, and Functions

- `const struct b43_phy_operations b43_phyops_g` is the driver-facing operation table. It wires allocation/free, prepare/init/exit, PHY/radio accessors, hardware power-control capability, RF kill, generic analog switching, channel switching, default channel, RX antenna selection, interference mitigation, TX-power recalc/adjust, and 15/60 second periodic work.
- `b43_gphy_op_allocate()` allocates `struct b43_phy_g` plus `struct b43_txpower_lo_control`, initializes the TSSI-to-dBm table, and stores the result in `dev->phy.g`.
- `b43_gphy_op_prepare_structs()` zeroes volatile state while preserving the allocated TSSI table and LO-control pointer. It initializes NRSSI sentinel values, the LO calibration list, OFDM table cache direction, average TSSI, default interference mode, and invalid calibration sentinels.
- `b43_phy_initg()`, `b43_phy_initb5()`, `b43_phy_initb6()`, `b43_phy_inita()`, and `b43_radio_init2050()` form the initialization core. They program revision-specific baseband/radio registers, run loopback/LO/radio calibrations, populate lookup tables, initialize power control, and apply workarounds.
- `b43_gphy_channel_switch()` writes the b/g channel code to `B43_MMIO_CHANNEL`, optionally runs the synthetic power-up workaround, and handles channel 14 host-flag/channel-extension behavior.
- `b43_set_txpower_g()`, `b43_gphy_op_recalc_txpower()`, `b43_gphy_op_adjust_txpower()`, `b43_put_attenuation_into_ranges()`, and `b43_generate_dyn_tssi2dbm_tab()` implement the software TX-power loop around TSSI, attenuation, LO bias/magnification, and SPROM power limits.
- `b43_calc_nrssi_offset()`, `b43_calc_nrssi_slope()`, `b43_calc_nrssi_threshold()`, and `b43_nrssi_mem_update()` maintain NRSSI calibration state and thresholds used for RSSI and interference decisions.
- `b43_radio_interference_mitigation_enable()` and `_disable()` save and restore stacks of PHY/radio/table registers for non-WLAN and manual WLAN interference mitigation modes.
- `b43_gphy_op_software_rfkill()` stores and restores RF override registers when the radio is powered down/up through the software RF kill path.

## Control Flow

Common b43 PHY setup calls `allocate`, then `prepare_structs`, then `prepare_hardware`, and finally `init`. `prepare_hardware` computes default baseband/radio attenuation, default TX control, RF/baseband attenuation lists, commits pending writes, and performs a special revision-1 reset sequence that temporarily disables `gmode`. `init` calls `b43_phy_initg()`, which selects the B5 or B6 baseband path, applies A/G common initialization when required, initializes loopback gain, runs radio 2050 calibration once or restores the cached calibration value, initializes LO state, calculates NRSSI state, initializes power control, and applies chip-specific OFDM restrictions.

Channel switching is intentionally small but side-effectful. The public callback validates channels 1..14, then writes the channel code through `b43_gphy_channel_switch()`. That helper may briefly tune to another channel for the synthetic power-up workaround, then writes `B43_MMIO_CHANNEL`. Channel 14 also toggles `B43_HF_ACPR` depending on SPROM country code and sets an extension-register bit; other channels clear the channel-14 related bits.

TX-power recalculation is two phase. `recalc_txpower` reads CCK and OFDM TSSI values from shared memory, merges them with `gphy->average_tssi`, estimates emitted power using `gphy->tssi2dbm`, clamps the requested power against SPROM maximums, and stores attenuation deltas if a change is needed. `adjust_txpower` later suspends the MAC, folds the deltas into current RF/baseband attenuation, applies radio-revision-specific `tx_control` transitions, locks PHY/radio access, calls `b43_set_txpower_g()`, and re-enables the MAC.

Periodic work also runs through the operations table. The 15-second path suspends the MAC, contains mostly placeholder ACI automation logic, and runs LO maintenance. The 60-second path recalculates NRSSI slope for boards with RSSI calibration data and performs a VCO channel hop on radio 2050 revision 8.

## State and Persistence

All persistent runtime state is in `dev->phy.g` and in the associated LO-control object. It is volatile kernel driver state, not on-disk persistence. The most important fields are current attenuation (`bbatt`, `rfatt`, `tx_control`), pending TX-power deltas, LO-control pointer/list, current/target/average TSSI, dynamic/static TSSI table selection, NRSSI slope/samples/lookup table, loopback gain components, interference mode and saved-register stack, cached OFDM-table address direction, RF kill saved override registers, and cached 2050 radio calibration value.

The code carefully saves and restores raw hardware registers around calibration, interference mitigation, and loopback measurement. Some saves are stored only on the stack within one function; longer-lived state such as `radio_off_context`, `interfstack`, `initval`, `lofcal`, and LO calibration lists persists across callbacks. `prepare_structs()` resets most runtime values but preserves allocation-owned pointers and tables.

Dynamic TSSI tables are allocated from SPROM PA coefficients and freed only when `dyn_tssi_tbl` is true. Static fallback table `b43_tssi2dbm_g_table` is shared and not freed. Allocation cleanup follows explicit error labels to avoid leaking LO or G-PHY state on partial failure.

## Dependencies and Integration Points

`phy_g.c` includes `b43.h`, `phy_g.h`, `phy_common.h`, `lo.h`, `main.h`, `wa.h`, and Linux `bitrev`/`slab`. It depends on core b43 MMIO, PHY, radio, OFDM-table, host-flag, shared-memory, dummy-transmission, MAC suspend/enable, channel-switch, and debug/error helpers. It also depends on SPROM fields such as PA coefficients, board flags, board vendor/type/revision, country code, max power, and idle TSSI.

The operation table is consumed by the b43 PHY dispatcher for G-PHY devices. LO-specific routines in `lo.c`, common A-PHY register definitions in `phy_a.h`, and common PHY operations in `phy_common.c` are tightly coupled to this file. Firmware/shared-memory integration appears in TSSI clearing and reading, RF attenuation shared-memory writes, and host-flag toggles for hardware power control and interference handling.

## Risks and Edge Cases

- The file is full of revision, radio, board, and SPROM conditionals. Regressions are likely if a change is tested on only one 2050 radio revision or only one board flag combination.
- Several paths use `B43_WARN_ON(1)` for unexpected register mode or revision combinations but continue with fallback values, which can mask unsupported hardware states.
- Register save/restore order is critical during NRSSI, loopback, radio calibration, and interference mitigation. Missing a restore can leave the radio deaf, overpowered, or miscalibrated.
- The interference stack is a fixed 26-entry packed array with comments noting it should be a data structure. Adding saved registers without increasing the size risks stack overflow warnings and failed restore.
- TX-power control mixes Q5.2 fixed point, SPROM values, RF/baseband attenuation ranges, and radio-revision-specific `tx_control` transitions. Off-by-one or sign errors can affect regulatory power behavior.
- ACI automation in `pwork_15sec` is largely TODO-gated; the manual and non-WLAN modes exist, but automatic mode is incomplete.
- Channel 14 and country-code handling is special and easy to break because it affects host flags and channel-extension bits in addition to the channel code.

## Test Signals

Useful validation signals include successful probe/init on representative G-PHY revisions, no allocation leaks on forced `kmalloc` failures, correct channel switch return values for channels 1..14 and `-EINVAL` outside that range, stable RF kill off/on cycles with `radio_off_context` restored, no MAC/PHY lock warnings around TX-power adjustment, TSSI shared-memory reads causing expected `B43_TXPWR_RES_*` transitions, and debug logs for TX power showing bounded attenuation changes. Hardware smoke tests should cover radio 2050 rev 8, non-rev8 2050, channel 14 country handling, boards with and without `B43_BFL_RSSI`, and interference mode enable/disable restore behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_g.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_g.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_g.h

## Purpose

`phy_g.h` is the private register and state contract for the b43 G-PHY implementation. It defines CCK and extended G-PHY register offsets, G-PHY table encodings, attenuation value types, TX-control bit meanings, and the `struct b43_phy_g` state block that `phy_g.c` stores under `dev->phy.g`.

The header does not implement the PHY algorithms, but it exposes the few G-PHY helpers needed by other b43 PHY code and declares `b43_phyops_g` for common PHY dispatch.

## Important APIs, Types, and Macros

- `B43_PHY_VERSION_CCK`, `B43_PHY_CCKBBANDCFG`, `B43_PHY_PGACTL`, `B43_PHY_ITSSI`, `B43_PHY_LO_LEAKAGE`, `B43_PHY_ENERGY`, `B43_PHY_DACCTL`, and `B43_PHY_RCCALOVER` name CCK/B-PHY registers used during G-PHY initialization, power measurement, LO leakage calibration, and attenuation programming.
- `B43_PHY_CLASSCTL`, `B43_PHY_GTABCTL`, `B43_PHY_GTABDATA`, `B43_PHY_LO_MASK`, `B43_PHY_LO_CTL`, `B43_PHY_RFOVER`, `B43_PHY_RFOVERVAL`, `B43_PHY_ANALOGOVER`, and `B43_PHY_ANALOGOVERVAL` name extended G-PHY registers used for classification, table access, LO control, RF override, and analog override.
- `B43_GTAB()`, `B43_GTAB_NRSSI`, `B43_GTAB_TRFEMW`, and `B43_GTAB_ORIGTR` encode G-PHY table numbers and offsets.
- `b43_gtab_read()` and `b43_gtab_write()` are external G-PHY table access helpers.
- `has_tx_magnification(phy)` and `has_loopback_gain(phy)` capture hardware capability predicates used by radio and gain setup.
- `struct b43_rfatt`, `struct b43_rfatt_list`, `struct b43_bbatt`, and `struct b43_bbatt_list` model radio and baseband attenuation choices and allowed ranges.
- `b43_compare_rfatt()` and `b43_compare_bbatt()` provide simple equality helpers for attenuation values.
- `B43_TXCTL_PA3DB`, `B43_TXCTL_PA2DB`, and `B43_TXCTL_TXMIX` are TX-control bits passed through the G-PHY TX-power path.
- `struct b43_phy_g` is the per-device G-PHY state object.
- `b43_gphy_set_baseband_attenuation()`, `b43_gphy_channel_switch()`, and `b43_generate_dyn_tssi2dbm_tab()` are callable helpers implemented in `phy_g.c`.
- `extern const struct b43_phy_operations b43_phyops_g` exports the operation table.

## Control Flow and Integration

`phy_common.c` selects `b43_phyops_g` for detected G-PHY hardware. The operation table calls into `phy_g.c`, which uses this header's register constants and `struct b43_phy_g` layout. Common code and neighboring PHY modules can also call the three declared helper functions for baseband attenuation, channel switching, and dynamic TSSI table generation.

The table macros are used with the generic b43 OFDM/G-PHY table helpers. The attenuation types are used by both G-PHY power control and LO calibration code. The capability macros are intentionally header-level so initialization and support code can make consistent radio-revision decisions.

## State and Persistence

`struct b43_phy_g` is volatile per-device state. It persists across callbacks after allocation and until the PHY is freed. Important fields include:

- ACI/interference flags: `aci_enable`, `aci_wlan_automatic`, `aci_hw_rssi`, and `interfmode`.
- RF kill state: `radio_on` and `radio_off_context` with saved RF override registers.
- TX-power state: `tssi2dbm`, `dyn_tssi_tbl`, target/current/average TSSI, current `bbatt`, `rfatt`, `tx_control`, and pending attenuation deltas.
- LO and loopback state: `lo_control`, `max_lb_gain`, `trsw_rx_gain`, `lna_lod_gain`, `lna_gain`, and `pga_gain`.
- Interference mitigation register stack: `interfstack[B43_INTERFSTACK_SIZE]`, currently a packed raw array.
- NRSSI calibration: `nrssi`, `nrssislope`, and `nrssi_lt`.
- Radio/init calibration sentinels: `lofcal` and `initval`.
- OFDM table access cache: `ofdmtab_addr` and `ofdmtab_addr_direction`.

The header comments identify several maturity risks: `interfstack` should be a data structure, `initval` needs a better name, and the table address cache must track last direction to avoid stale hardware address reuse.

## Dependencies

The header includes `phy_a.h` because OFDM PHY registers are shared with A-PHY definitions and needed for G-PHY register encodings. It assumes b43 core types such as `struct b43_wldev`, `struct b43_phy_operations`, `u8`, `u16`, `s8`, `s16`, `s32`, and `bool` are available through kernel and b43 headers. The forward declaration of `struct b43_txpower_lo_control` links this header to `lo.h` without requiring the full LO definition.

## Risks and Edge Cases

- The register constants are raw hardware ABI. A wrong value can silently corrupt unrelated PHY/radio state.
- `B43_INTERFSTACK_SIZE` must remain large enough for every save in interference mitigation; the packed format stores only 12 offset bits and 4 register-id bits.
- `has_tx_magnification()` and `has_loopback_gain()` encode subtle revision/radio predicates. Changes should be validated against all affected radio revisions.
- The dynamic TSSI table pointer can either be static or allocated. Callers must respect `dyn_tssi_tbl` before freeing.
- Header state fields are heavily coupled to `phy_g.c`; changing layout or initialization assumptions can break calibration restore and periodic work.

## Test Signals

Compile coverage should include `CONFIG_B43_PHY_G` and LO support. Runtime signals include successful allocation/free without leaks, no NULL `lo_control` or `tssi2dbm` use after `prepare_structs`, valid attenuation range generation, successful channel changes through `b43_gphy_channel_switch`, and no restore warnings from interference stack users. Static analysis should check that every dynamic TSSI table allocation is paired with the `dyn_tssi_tbl` guarded free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_g.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ht.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ht.c

## Purpose

`phy_ht.c` implements the b43 HT-PHY backend for Broadcom 802.11n-era devices. It focuses on BCMA bus devices with 2059 radio hardware. The file handles HT PHY allocation, table upload, radio 2059 initialization, RF sequencing, channel setup through HT channel tables, CCA reset, per-core AFE/RSSI/sample control, TSSI measurement, and per-core TX power-control register setup.

The exported `b43_phyops_ht` table integrates this backend with the common b43 PHY layer. Several callbacks are placeholders or minimal implementations, reflecting that this HT support is incomplete compared with the older G-PHY path.

## Important APIs, Types, and Functions

- `const struct b43_phy_operations b43_phyops_ht` wires allocation/free, prepare/init, PHY maskset, radio read/write, software RF kill, analog switching, channel switching, default channel, and TX-power callbacks.
- `b43_phy_ht_op_allocate()`, `_prepare_structs()`, and `_free()` manage `struct b43_phy_ht`, initialize TX power control as enabled, mark per-core TX power index as invalid, and initialize saved baseband multipliers to `-1`.
- `b43_phy_ht_op_init()` is the main initialization sequence. It verifies BCMA, uploads HT tables, clears and programs many PHY/HT table registers, initializes AFE, performs RF sequences, optionally initializes B-PHY compatibility registers for 2 GHz, and configures TX power control.
- `b43_radio_2059_init()`, `_init_pre()`, `_rcal()`, `_rccal()`, and `b43_radio_2059_channel_setup()` program and calibrate the 2059 radio using data from `radio_2059.h` and `tables_phy_ht.h`.
- `b43_phy_ht_set_channel()`, `_channel_setup()`, and `_spur_avoid()` select channel-table entries, program bandwidth registers, toggle 2/5 GHz band control, reset B-PHY as needed, update classifier bits, and update BCMA PLL spur avoidance.
- `b43_phy_ht_force_rf_sequence()` triggers RF state-machine sequences and polls for completion.
- `b43_phy_ht_tx_power_ctl_idle_tssi()`, `_setup()`, `_ctl()`, `_tssi_setup()`, and `_tx_power_fix()` configure per-core TSSI and target-power state based on SPROM core power information.
- `b43_phy_ht_load_samples()`, `_run_samples()`, `_stop_playback()`, and `_tx_tone()` support sample playback used for idle TSSI measurement.
- `b43_phy_ht_rssi_select()` and `_poll_rssi()` configure per-core RSSI/TSSI selection and collect signed 6-bit RSSI samples.

## Control Flow

The driver enters through `b43_phyops_ht`. Allocation installs `dev->phy.ht`; preparation resets it and seeds default TX power-control state. Initialization rejects non-BCMA devices, loads PHY tables, programs baseband/AFE/classifier registers, copies selected HT table values, resets CCA, enables the MAC/PHY clock, forces RX2TX and reset-to-RX RF sequences around PA override state, initializes B-PHY compatibility logic for 2 GHz, writes late HT table data, then temporarily disables TX power control while it measures idle TSSI and programs per-core power-control tables.

RF kill is asymmetric. Blocking clears the radio power-up bit in `B43_PHY_HT_RF_CTL_CMD`; unblocking reinitializes radio 2059 when present and switches back to the current channel. The function expects the MAC to be suspended and logs an error if it is not.

Channel switching is routed through the current mac80211 channel definition, not directly through the `new_channel` value except for validation. Only 2 GHz validation is implemented in `b43_phy_ht_op_switch_channel`; 5 GHz currently returns `-EINVAL` there even though lower-level setup code has 5 GHz register paths. `b43_phy_ht_set_channel()` supports only radio version `0x2059` and returns `-ESRCH` if no channel-table entry exists.

TX power control is mostly an initialization-time hardware setup. Recalculation returns `B43_TXPWR_RES_DONE` and adjustment is empty. The setup path computes target powers and PA polynomial coefficients from SPROM `core_pwr_info` for 2 GHz and 5 GHz low/mid/high bands, writes target and idle TSSI registers, and bulk-writes 64-entry per-core power tables.

## State and Persistence

`struct b43_phy_ht` persists under `dev->phy.ht` until free. It stores:

- `rf_ctl_int_save[3]` for PA override save/restore around forced RF sequences.
- `tx_pwr_ctl` as the desired software view of hardware TX power-control enablement.
- `tx_pwr_idx[3]` as saved per-core power-control indices when disabling/enabling hardware control.
- `bb_mult_save[3]` as saved baseband multipliers restored after sample playback.
- `idle_tssi[3]` as per-core idle TSSI values measured by sample playback and later programmed into power-control registers.

Most other state is transient in hardware registers and tables. The file frequently saves local register arrays around RSSI polling and idle TSSI measurement, then restores them before returning. The channel tables are static data supplied by `tables_phy_ht`/`radio_2059`.

## Dependencies and Integration Points

The file includes `b43.h`, `phy_ht.h`, `tables_phy_ht.h`, `radio_2059.h`, and `main.h`. It depends on Linux allocation, BCMA chipcommon/PMU/PLL helpers, mac80211 channel/band state, SPROM per-core power data, b43 PHY/radio/table helpers, MAC/PHY clock helpers, and common RF/channel dispatch.

`b43_phy_ht_get_channeltab_e_r2059()`, `b43_phy_ht_tables_init()`, `b43_httab_*()` helpers, and `r2059_upload_inittabs()` are key external table/radio dependencies. `b43_phyops_ht` is consumed by the common PHY dispatcher for HT PHY hardware.

## Risks and Edge Cases

- HT-PHY is explicitly limited to BCMA in init. Non-BCMA devices fail with `-EOPNOTSUPP`.
- Many TODO/FIXME markers remain: unconditional radio calibration, uncertain 5 GHz PA override value, unverified AFE masks, sample command mask uncertainty, incomplete RSSI selection types, questionable table index `40`, and uncertain spur avoidance scope.
- RF sequence waits sleep or poll with fixed limits and only log on timeout. A timeout may leave hardware in an unexpected state.
- `b43_phy_ht_op_switch_channel()` rejects 5 GHz at the operation boundary despite lower-level band-control support.
- Recalc/adjust TX-power callbacks are stubs, so runtime power correction depends on the hardware setup rather than a software feedback loop.
- RSSI selection for core off and most RSSI types is unimplemented and logs errors.
- Channel switching ignores `new_channel` except validation and uses the current chandef pointer, so caller ordering matters.

## Test Signals

Validation should include BCMA HT hardware with 2059 radio, successful table upload, radio init without `rcal`/`rccal` timeout logs, RF sequence completion without timeout, channel table lookup success for supported channels, CCA reset after spur avoidance, and idle TSSI values populated for all three cores. Compile tests should cover `CONFIG_B43_PHY_HT`. Runtime tests should verify RF kill requires MAC suspension, 2 GHz channel switches work through mac80211 chandef state, 5 GHz behavior is either intentionally rejected or fixed, and no HT sample playback leaves stale `bb_mult_save` state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ht.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ht.h

## Purpose

`phy_ht.h` defines the register map, small data structures, and exported operation table declaration for b43 HT-PHY support. It is the shared hardware contract used by `phy_ht.c` and HT table/channel code.

The file names baseband, band-control, table-access, classifier, sample-playback, TSSI, bandwidth, TX power-control, RSSI, RF sequence, RF control, AFE, and B-PHY compatibility registers. It also defines the per-channel PHY register tuple used by radio 2059 channel tables and the per-device HT state block.

## Important APIs, Types, and Register Groups

- `B43_PHY_HT_BBCFG` plus `RSTCCA` and `RSTRX` bits control HT baseband reset behavior.
- `B43_PHY_HT_BANDCTL` and `B43_PHY_HT_BANDCTL_5GHZ` select 2 GHz versus 5 GHz operation.
- `B43_PHY_HT_TABLE_ADDR`, `B43_PHY_HT_TABLE_DATALO`, and `B43_PHY_HT_TABLE_DATAHI` provide HT table access.
- `B43_PHY_HT_CLASS_CTL` and its CCK/OFDM/waited bits gate the PHY classifier.
- `B43_PHY_HT_SAMP_*` and `B43_PHY_HT_IQLOCAL_CMDGCTL` control sample playback and IQ-local command behavior.
- `B43_PHY_HT_TSSIMODE`, `B43_PHY_HT_TXPCTL_*`, and `B43_PHY_HT_TX_PCTL_STATUS_*` define per-core TSSI/TX power-control registers and bit fields.
- `B43_PHY_HT_RSSI_C1`, `_C2`, and `_C3` expose per-core RSSI sample registers.
- `B43_PHY_HT_BW1` through `B43_PHY_HT_BW6` are the channel-dependent PHY bandwidth values.
- `B43_PHY_HT_RF_SEQ_*` registers and bits control the RF state machine.
- `B43_PHY_HT_AFE_*` and `B43_PHY_HT_RF_CTL_INT_*` name per-core analog/RF control override registers.
- `B43_PHY_B_BBCFG` and `B43_PHY_HT_TEST` cover B-PHY compatibility behavior used when HT operates in 2 GHz.
- `struct b43_phy_ht_channeltab_e_phy` groups six bandwidth register values supplied by HT channel tables.
- `struct b43_phy_ht` stores per-device HT runtime state.
- `extern const struct b43_phy_operations b43_phyops_ht` exports the HT operation table.

## Control Flow and Integration

The header is included by `phy_ht.c`, which consumes nearly every register definition during init, RF sequencing, channel switching, sample playback, RSSI polling, and TX power setup. `radio_2059.h` channel entries embed `struct b43_phy_ht_channeltab_e_phy`, allowing a radio-channel table lookup to return both radio synthesizer values and the PHY bandwidth tuple required by `b43_phy_ht_channel_setup()`.

Common b43 PHY dispatch uses `b43_phyops_ht` for HT PHY devices when the build enables HT support. The state structure is hung from `dev->phy.ht` and initialized by the HT operation callbacks.

## State and Persistence

`struct b43_phy_ht` is volatile per-device state. It contains:

- `rf_ctl_int_save[3]`, used to preserve per-core RF control interrupt/PA override registers while forcing RF sequences.
- `tx_pwr_ctl`, the software-desired enable state for hardware TX power control.
- `tx_pwr_idx[3]`, saved/restored per-core TX power-control index values.
- `bb_mult_save[3]`, saved baseband multipliers used by sample playback and restored by `b43_phy_ht_stop_playback()`.
- `idle_tssi[3]`, measured per-core idle TSSI values used by power-control setup.

This state is reset in `prepare_structs()`, not persisted across device teardown, and must remain consistent with the register layouts in the same header.

## Dependencies

The header includes `phy_common.h` for b43 PHY declarations and register encoding helpers. It relies on kernel integer types and b43's `B43_PHY_OFDM()`, `B43_PHY_EXTG()`, and `B43_PHY_N_BMODE()` macros. It is coupled to `tables_phy_ht.h` and `radio_2059.h` because channel-table entries carry `struct b43_phy_ht_channeltab_e_phy` values.

## Risks and Edge Cases

- Register constants are raw hardware ABI. Incorrect masks in the header can cause broad hardware misconfiguration.
- TX power-control bit definitions are shared by three cores but some masks are named with C1 even when reused for C2/C3. Callers must be clear about which registers have identical bit layouts.
- `bb_mult_save` uses signed sentinel behavior in `phy_ht.c`; it is declared `s32`, so changing type would break the `-1` invalid marker.
- The header exposes 5 GHz band-control and target-power fields, but current operation-level channel switching in `phy_ht.c` rejects 5 GHz. Tests should catch any mismatch between declared capability and callback behavior.

## Test Signals

Compile tests should verify HT support with `phy_ht.c`, `tables_phy_ht.c`, and `radio_2059.h`. Runtime signals include clean writes to HT table data ports, correct B-PHY reset behavior when switching bands, per-core idle TSSI capture, RF sequence completion, and TX power-control register writes matching the bit masks defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lcn.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lcn.c

## Purpose

`phy_lcn.c` implements the b43 LCN-PHY backend for Broadcom 802.11n LCN devices, primarily around radio 2064 and 2 GHz operation. It performs LCN allocation, baseband/radio init, channel setup, spur avoidance, AFE toggling, TX gain and initial TX power-control setup, temperature/voltage sense setup, IIR filter loading, RF kill, analog switching, and low-level PHY/radio access.

The exported `b43_phyops_lcn` operation table connects this code to the common PHY dispatcher. Like HT support, parts of LCN behavior are incomplete and marked with TODO/FIXME comments.

## Important APIs, Types, and Functions

- `const struct b43_phy_operations b43_phyops_lcn` provides allocation/free, prepare/init, PHY maskset, radio read/write, RF kill, analog switch, channel switch, default channel, and TX-power callbacks.
- `b43_phy_lcn_op_allocate()`, `_prepare_structs()`, and `_free()` manage `struct b43_phy_lcn` under `dev->phy.lcn`.
- `b43_phy_lcn_op_init()` initializes PHY registers, uploads LCN tables, runs rev0 baseband init and board-unit tweaks, initializes radio 2064, initializes TX power control for 2 GHz, switches to the current channel, and applies BCMA chip control writes.
- `b43_radio_2064_init()` and `b43_radio_2064_channel_setup()` program the radio 2064 registers used by LCN hardware.
- `b43_phy_lcn_set_channel()` and `_set_channel_tweaks()` perform channel-specific PLL/PMU/spur avoidance programming, radio tuning, AFE toggling, SFO configuration, CCK/OFDM transmit IIR filter selection, and table/register updates.
- `b43_phy_lcn_tx_pwr_ctl_init()`, `_set_tx_gain()`, `_set_tx_gain_override()`, `_set_bbmult()`, `_set_dac_gain()`, and `_clear_tx_power_offsets()` configure software-selected initial TX gain and power table state.
- `b43_phy_lcn_sense_setup()` temporarily saves many radio/PHY registers, suspends the MAC, configures auxiliary sense paths for temperature or VBAT, triggers a dummy transmission, restores registers, and resumes the MAC.
- `b43_phy_lcn_load_tx_iir_cck_filter()` and `_ofdm_filter()` select hardcoded filter coefficient sets by type and write them to PHY registers.
- `b43_phy_lcn_op_software_rfkill()` and `_switch_analog()` control radio/AFE power-down bits.

## Control Flow

After allocation and structure reset, initialization writes early PHY reset/AFE bits, initializes LCN tables, runs baseband and BU tweak sequences, initializes radio 2064 when the radio version matches, and starts TX power-control initialization in 2 GHz. It then calls the common channel switch for the current channel and programs BCMA chipcommon register-control/chip-control values.

Channel switching is operation-level limited to 2 GHz channels 1..14. The lower-level `b43_phy_lcn_set_channel()` first applies PLL/spur tweaks based on channel ranges, toggles the reset-like `0x44a` sequence, runs radio channel setup, delays, toggles AFE power, writes per-channel SFO constants, chooses a special channel-14 CCK IIR filter or normal channel filter type 25, writes an OFDM filter, and sets a final table-related PHY field.

TX power setup currently chooses fixed gain values and BB multiplier when hardware power control is not capable. If `hw_pwr_ctl_capable` is set, it logs that TX power control is not supported for this hardware. Recalc and adjust callbacks are stubs returning done/no-op, so the main dynamic behavior is the initial setup rather than a feedback loop.

RF kill expects a suspended MAC and logs if the MAC is enabled. Blocking writes multiple RF control override fields to power down portions of the radio path; unblocking clears those override bits rather than rerunning full radio init.

## State and Persistence

`struct b43_phy_lcn` is small and volatile. It stores:

- `hw_pwr_ctl`, whether hardware power control is enabled.
- `hw_pwr_ctl_capable`, whether hardware power control should be possible.
- `tx_pwr_curr_idx`, the current TX power index used by sense/setup paths.

Most LCN state lives directly in hardware registers or tables. `b43_phy_lcn_sense_setup()` has extensive local save/restore arrays for radio/PHY registers so temporary sense configuration does not persist. Channel and filter state persists in hardware after channel switching. `prepare_structs()` zeros the state each time the PHY is prepared.

## Dependencies and Integration Points

The file includes `b43.h`, `phy_lcn.h`, `tables_phy_lcn.h`, `main.h`, and Linux slab allocation. It depends on BCMA chipcommon/PMU helpers, mac80211 band/channel state, SPROM board flags and board revision, b43 PHY/radio/table helpers, MAC suspend/enable, dummy transmission, and common channel dispatch.

`b43_phy_lcn_tables_init()` and `b43_lcntab_write()` supply table initialization and table writes. `b43_phyops_lcn` is the integration point used by common b43 PHY selection for LCN devices.

## Risks and Edge Cases

- The file has many TODO/FIXME comments, including missing radio channel setup pieces, missing radio-init wait condition, hardcoded sense/table values, uncertain BU tweaks, and unimplemented TX power recalculation.
- Operation-level channel switching rejects 5 GHz; radio init has an explicit 5 GHz TODO.
- `b43_phy_lcn_tx_pwr_ctl_init()` logs unsupported hardware if `hw_pwr_ctl_capable` is true, which suggests the capable path is not implemented.
- `b43_phy_lcn_sense_setup()` saves register `0x4d0` twice in its save array, likely harmless but a maintenance smell.
- The CCK/OFDM IIR filter tables are hardcoded with comments noting brcmsmac was outdated and other values may need updating.
- RF kill and analog switching directly manipulate override bits and depend on caller suspension discipline.

## Test Signals

Validation should cover LCN allocation/init on radio 2064, successful LCN table upload, channel switches 1..14 with `-EINVAL` outside range, channel 14 selecting CCK filter type 3, normal channels selecting type 25 and OFDM type 0, no MAC enabled log during RF kill, and successful MAC suspend/resume around sense setup. Hardware logs should be checked for unsupported TX power-control messages and for correct PLL/spur behavior on channels 1..4/9..12 versus the other channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lcn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lcn.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lcn.h

## Purpose

`phy_lcn.h` defines the small LCN-PHY register/state interface used by `phy_lcn.c`. It names the LCN AFE/RF/table access registers, declares the per-device LCN state structure, and exports the `b43_phyops_lcn` operation table.

The header is intentionally compact compared with G/HT/LP headers. Most LCN register use in `phy_lcn.c` is still raw numeric offsets; this header only names the common AFE, RF control, and table port registers.

## Important APIs, Types, and Macros

- `B43_PHY_LCN_AFE_CTL1` and `B43_PHY_LCN_AFE_CTL2` are AFE control registers used for analog power toggling and AFE set/unset sequencing.
- `B43_PHY_LCN_RF_CTL1` through `B43_PHY_LCN_RF_CTL7` name RF control registers manipulated by software RF kill.
- `B43_PHY_LCN_TABLE_ADDR`, `B43_PHY_LCN_TABLE_DATALO`, and `B43_PHY_LCN_TABLE_DATAHI` define the LCN table access ports used for TX power offset clearing and table operations.
- `struct b43_phy_lcn` stores LCN runtime power-control state: `hw_pwr_ctl`, `hw_pwr_ctl_capable`, and `tx_pwr_curr_idx`.
- `extern const struct b43_phy_operations b43_phyops_lcn` exports the operation table implemented in `phy_lcn.c`.

## Control Flow and Integration

Common b43 PHY dispatch selects `b43_phyops_lcn` for LCN PHY devices. The operation callbacks allocate and prepare `struct b43_phy_lcn`, then `phy_lcn.c` uses the register constants in this header during initialization, channel switching, RF kill, analog switching, table clearing, and radio/PHY access.

The table access constants are used directly by routines that stream zeros into LCN TX power offset tables. The RF control constants are used by RF kill to set and clear power-down override bits. The AFE control constants are used by both analog switching and the AFE power-cycle helper.

## State and Persistence

The LCN state structure is volatile and per-device. It is allocated during PHY allocation, zeroed in `prepare_structs()`, and freed on PHY teardown. Its fields are a software mirror/control surface for TX power behavior; current code mostly uses them to choose the fixed software TX gain path and to remember the current TX power index during sense setup.

No on-disk persistence exists. Hardware state persists only in the programmed PHY/radio registers until reset, channel switch, RF kill, or another init path changes it.

## Dependencies

The header includes `phy_common.h` for common b43 PHY types and register encodings. It relies on `B43_PHY_OFDM()` for register address construction and forward-declares `struct b43_phy_operations`. It is consumed by `phy_lcn.c`, `tables_phy_lcn.c`, and common PHY selection code.

## Risks and Edge Cases

- The header names only a subset of LCN registers; most raw offsets still live in `phy_lcn.c`, which makes audits and refactors harder.
- `hw_pwr_ctl_capable` exists, but the implementation logs that hardware TX power control is unsupported when it is set. Consumers should not assume this field means the path works.
- `tx_pwr_curr_idx` has no explicit nonzero initializer in the header or prepare path; code that restores the TX power index must tolerate the default zero.
- RF kill relies on the exact RF control bit masks in `phy_lcn.c`; changing these constants requires hardware validation.

## Test Signals

Compile tests should include LCN support and table code. Runtime checks should verify `dev->phy.lcn` is allocated, zeroed, and freed correctly; AFE control writes hit the expected registers; RF kill changes only the intended RF control registers; and LCN table clearing writes through the named table address/data ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lcn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lp.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lp.c

## Purpose

`phy_lp.c` implements the b43 LP-PHY backend for Broadcom low-power 802.11a/g hardware. It supports SSB-only LP PHY devices, 2062 and 2063 radios, 2 GHz and 5 GHz channel tables, SPROM-derived power/RSSI setup, baseband/radio initialization, RC calibration, channel tuning, antenna selection, RF kill, analog switching, TX gain and TX power-control setup, RX IQ calibration, sample/tone generation, periodic calibration, and low-level PHY/radio access.

The file is significantly more complete than LCN in some areas, but many paths still have TODO/FIXME markers, especially hardware TX power control, ACI, calibration details, and spec ambiguities.

## Important APIs, Types, and Functions

- `const struct b43_phy_operations b43_phyops_lp` wires allocation/free, prepare/init, PHY maskset, radio read/write, RF kill, analog switch, channel switch, default channel, RX antenna selection, TX-power recalc/adjust stubs, and 15/60 second periodic work.
- `b43_lpphy_op_allocate()`, `_prepare_structs()`, and `_free()` manage `struct b43_phy_lp`, setting default antenna state after zeroing.
- `b43_lpphy_op_init()` is the lifecycle entry point. It rejects non-SSB devices, reads band-specific SPROM data, initializes baseband and radio, calibrates RC, switches initially to channel 7, initializes TX power control, and runs calibration.
- `lpphy_read_band_sprom()` transfers SPROM isolation, PA, RSSI, max-power, and per-rate power-offset data into `dev->phy.lp`.
- `lpphy_table_init()`, `lpphy_baseband_rev0_1_init()`, `lpphy_baseband_rev2plus_init()`, and `lpphy_baseband_init()` upload LP tables and configure revision-specific baseband/RSSI/AFE/TR lookup state.
- `lpphy_2062_init()`, `lpphy_2063_init()`, `lpphy_radio_init()`, `lpphy_b2062_tune()`, and `lpphy_b2063_tune()` initialize and tune radio hardware. Static `b2062_chantbl` and `b2063_chantbl` provide channel-specific data.
- `lpphy_calibrate_rc()`, `lpphy_rev0_1_rc_calib()`, `lpphy_rev2plus_rc_calib()`, `lpphy_set_rc_cap()`, and `lpphy_loopback()` handle RC and loopback calibration.
- `lpphy_set_tx_power_control()`, `lpphy_tx_pctl_init_hw()`, `lpphy_tx_pctl_init_sw()`, `lpphy_tx_pctl_init()`, and `lpphy_set_tx_power_by_index()` manage TX power-control mode, table-selected gains, BB multiplier, IQ coefficients, and RF power overrides.
- `lpphy_rx_iq_cal()`, `lpphy_calc_rx_iq_comp()`, `lpphy_run_ddfs()`, `lpphy_start_tx_tone()`, `lpphy_stop_tx_tone()`, and `lpphy_papd_cal_txpwr()` implement calibration support using IQ estimates and generated tones.
- `b43_lpphy_op_switch_channel()` dispatches to the proper radio tune function, applies analog filter and gain-table updates for 2062, persists `lpphy->channel`, and writes `B43_MMIO_CHANNEL`.

## Control Flow

The common PHY layer enters through `b43_phyops_lp`. Allocation installs `dev->phy.lp`; preparation clears all LP state and sets default antenna. Init requires `B43_BUS_SSB`; otherwise it returns `-EOPNOTSUPP`. On supported hardware it reads SPROM band fields into LP state, initializes table/baseband state according to PHY revision, initializes the radio according to radio version, performs RC calibration, switches to channel 7, initializes TX power control, runs a broader calibration path, and leaves later operation to channel, RF kill, antenna, and periodic callbacks.

Baseband initialization is split by revision. Rev0/1 setup programs AFE, CRS, clipping, RSSI, TR lookup, FEM/BT flags, PAREF, PMU, and 2 GHz/5 GHz differences. Rev2+ setup uses a different register set, optionally writes board-revision and chip-specific tables, saves digital filter state, and configures AFE/RSSI registers differently.

Radio channel switching is table-driven. 2062 tuning finds a `b2062_chantbl` entry, writes tune registers, calculates PLL values from crystal frequency and `lpphy->pdiv`, calibrates VCO, and returns `-EIO` if the fallback VCO calibration still reports failure. 2063 tuning finds a `b2063_chantbl` entry, writes radio front-end values, computes PLL calibration values with fixed-point division, runs VCO calibration, and restores a saved register. Invalid channels return `-EINVAL`.

Calibration paths suspend or deafen receive behavior as needed, save old overrides/gains/TX power mode, run loopback or IQ estimation, and restore state. `lpphy_calibration()` is also the 60-second periodic hook; it turns off TX power control, optionally runs workarounds/full calibration, restores digital filters for rev2+, runs RX IQ calibration, and re-enables the MAC.

## State and Persistence

`struct b43_phy_lp` is the primary runtime state. It persists under `dev->phy.lp` until free and is reset by `prepare_structs()`. Important fields populated from SPROM include transmit isolation, max TX power by band, per-rate max power arrays, PA coefficients, RSSI offsets/calibration values, and BX architecture. Runtime/calibration fields include `txpctl_mode`, TSSI index/NPT/count, target TX frequency, TX power index override, `rc_cap`, `full_calib_chan`, best IQ-local coefficients, saved digital filter state, CRS disable reference flags, PLL divider `pdiv`, current channel, active antenna, and active TX tone frequency.

The file has many local save/restore blocks around calibration. `lpphy_pr41573_workaround()` is especially stateful: it saves a 256-entry TX power table region, power-control mode, override index, TSSI fields, reruns partial init/calibration/RF state, restores the table and channel, restores antenna and RC cap, and writes the saved TX power-control mode back.

Hardware state is programmed through PHY/radio registers and LP tables. There is no persistent storage beyond SPROM input and volatile driver memory. Several header fields have FIXME comments about initial values; callers must ensure init paths populate them before depending on them.

## Dependencies and Integration Points

The file includes `b43.h`, `main.h`, `phy_lp.h`, `phy_common.h`, `tables_lpphy.h`, Linux `cordic`, and Linux `slab`. It depends on SSB chipcommon/PMU helpers, SPROM data, b43 PHY/radio/table accessors, MAC suspend/enable, host flags, MMIO channel writes, dummy transmission, mac80211 band state, and LP table upload helpers such as `lpphy_rev0_1_table_init()`, `lpphy_rev2plus_table_init()`, `lpphy_init_tx_gain_table()`, `b2062_upload_init_table()`, and `b2063_upload_init_table()`.

The exported operation table is consumed by common PHY dispatch for LP PHY devices. The implementation is tightly coupled to `phy_lp.h` register constants and `struct b43_phy_lp`, and it shares generic PHY operation expectations with the other b43 PHY backends.

## Risks and Edge Cases

- Init is SSB-only. Any BCMA LP device fails with `-EOPNOTSUPP`.
- Many TODO/FIXME comments remain: incomplete prepare state, cached host-flag write concern, PMU recalibration, channel 14 analog filter uncertainty, hardware TX power-control capability disabled behind `if (0)`, missing NPT/offset/target-power work, missing ACI init, and empty TX-power recalc/adjust/15-second work.
- Some calculations rely on crystal frequency and PMU capability. The code warns if PMU capability or crystal frequency is absent but still uses derived values.
- Calibration loops can sleep/poll for long periods. Timeout behavior is limited and can leave partially restored radio state if not carefully audited.
- `lpphy_start_tx_tone()` has an explicit FIXME about negative frequency semantics and warns if sample count exceeds 63.
- Static channel tables are large and hardware ABI sensitive. Missing channel entries return `-EINVAL`; bad entries can misprogram PLL/radio state.
- `lpphy_calc_rx_iq_comp()` performs integer fixed-point math and square root on values derived from hardware accumulators; divide-by-zero and sign/overflow assumptions should be treated carefully.
- TX power-control mode writes include a suspicious `((u16)lpphy->tssi_npt << 16)` expression that shifts out of a 16-bit value before maskset semantics, matching a TODO-heavy area.

## Test Signals

Validation should include SSB LP devices with 2062 and 2063 radios, rev0/1 and rev2+ PHY revisions, both 2 GHz and 5 GHz channel tables, invalid channel rejection, VCO calibration fallback on 2062, RC calibration completion, channel field persistence, antenna selection on rev0/1, RF kill on/off, and periodic 60-second calibration. Memory-failure testing should cover `b43_lpphy_op_allocate()` and `lpphy_pr41573_workaround()` allocation failure. Hardware logs should be checked for `B43_WARN_ON` hits, channel 7 init-switch failures, and unexpected TX power-control mode warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lp.c -->

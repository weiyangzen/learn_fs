# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lp.h

## Purpose

`phy_lp.h` is the private LP-PHY hardware contract for the Broadcom b43 wireless driver. It does not implement behavior directly; instead it names the memory-mapped PHY registers, Broadcom 2062/2063 radio registers, TX power-control modes, LP-specific mutable driver state, and the `b43_phyops_lp` operation table exported by `phy_lp.c`.

The file is used by the LP PHY implementation and LP table loader to keep raw register offsets out of the procedural code. It covers both CCK and OFDM LP-PHY register windows via `B43_PHY_CCK()` and `B43_PHY_OFDM()`, radio access decorations for 2062 north/south register banks, and the single-radio 2063 register map. These constants are the vocabulary used by initialization, tuning, calibration, RF kill, antenna selection, gain control, TSSI/TX power control, and periodic calibration paths.

## Important APIs, Types, and Register Groups

The header exports several categories of symbols:

- `B43_LPPHY_B_*` and other CCK-range constants define LP-PHY CCK baseband registers, including B PHY version/config/status, CCK channel selection, RSSI/TSSI controls, IQ thresholds, gain tables, sync detection, DSSS/CCK coefficients, optional modes, and low-level gain/energy registers.
- `B43_LPPHY_*` OFDM-range constants define the main LP-PHY register set, including BB configuration, CRS and power thresholds, OFDM sync, AFE controls, radar detection, RF override registers, LP PHY reset/clock control, table address/data ports, IQ estimation accumulators, TX power-control registers, GPIO registers, and unknown initialization-only registers such as `B43_LPPHY_4C3` through `B43_LPPHY_4C5`.
- `B43_LPPHY_TX_PWR_CTL_CMD_MODE`, `_OFF`, `_SW`, and `_HW` are bit definitions for the hardware TX power-control mode stored in `B43_LPPHY_TX_PWR_CTL_CMD`.
- `B43_LP_RADIO()`, `B43_LP_NORTH()`, and `B43_LP_SOUTH()` decorate radio register numbers. The 2062 radio has north and south banks, with the south bank ORed with `0x4000`; 2063 registers are single-bank.
- `B2062_N_*`, `B2062_S_*`, and `B2063_*` define the raw radio register addresses consumed by radio init tables, channel tuning, PLL setup, RX/TX front-end setup, calibration, TSSI muxing, and AFE control.
- `enum b43_lpphy_txpctl_mode` is the driver-side state enum for TX power control: unknown, off, software, or hardware. It maps onto the hardware mode bits above.
- `struct b43_phy_lp` is the private per-device LP PHY state hung from `dev->phy.lp`. It caches SSB SPROM-derived power/RSSI calibration data, runtime channel and antenna state, TX power-control state, RC calibration state, temporary digital filter snapshots, CRS disable flags, and calibration/tone metadata.
- `enum tssi_mux_mode` identifies TSSI measurement mux positions: pre-PA, post-PA, or external.
- `extern const struct b43_phy_operations b43_phyops_lp` is the LP PHY operation table selected by `phy_common.c` for `B43_PHYTYPE_LP` when `CONFIG_B43_PHY_LP` is enabled.

There are no callable functions defined in the header besides macros and type declarations. Runtime behavior is implemented in `phy_lp.c` and table behavior in `tables_lpphy.c`.

## Control Flow and Runtime Integration

LP PHY devices enter through the common b43 PHY allocation flow. `phy_common.c` maps `B43_PHYTYPE_LP` to `b43_phyops_lp`; the operation table in `phy_lp.c` then provides allocation, initialization, channel switching, RF kill, analog switching, radio read/write, antenna selection, TX power recalculation, and periodic work hooks.

The high-level LP PHY lifecycle is:

1. `b43_lpphy_op_allocate()` allocates zeroed `struct b43_phy_lp` and stores it in `dev->phy.lp`.
2. `b43_lpphy_op_prepare_structs()` clears the structure and sets `antenna` to `B43_ANTENNA_DEFAULT`.
3. `b43_lpphy_op_init()` rejects non-SSB devices, reads LP band/SPROM calibration fields into `struct b43_phy_lp`, initializes baseband and radio hardware, runs RC calibration, switches initially to channel 7, initializes TX power control, and runs LP calibration.
4. `b43_lpphy_op_switch_channel()` chooses 2063 or 2062 tune routines based on `dev->phy.radio_ver`; for 2062 it also updates analog filters and gain tables. It persists the chosen channel in `lpphy->channel` and writes `B43_MMIO_CHANNEL`.
5. Periodic and calibration paths restore cached runtime state such as TX power override, TSSI state, RC cap, active channel, and antenna after hardware reset or calibration sequences.

The register definitions in this header are used throughout those flows. Examples include `B43_LPPHY_AFE_CTL_OVR` and `B43_LPPHY_AFE_CTL_OVRVAL` for analog on/off and calibration override state; `B43_LPPHY_RF_OVERRIDE_0`, `_VAL_0`, `_2`, and `_2_VAL` for radio override sequences; `B43_LPPHY_TX_PWR_CTL_*` for TX power-control mode/index/target state; `B43_LPPHY_TABLE_ADDR`, `B43_LPPHY_TABLEDATALO`, and `B43_LPPHY_TABLEDATAHI` for LP table access; and `B2062_*`/`B2063_*` registers for upload/tune/calibration logic.

## State and Persistence Behavior

`struct b43_phy_lp` is volatile driver state, not on-disk persistence. It is allocated per wireless device, initialized from SPROM and hardware state, updated during channel changes and calibration, and freed when the PHY is released.

Important state fields:

- `txpctl_mode` mirrors the hardware TX power-control mode. `phy_lp.c` reads it from `B43_LPPHY_TX_PWR_CTL_CMD`, updates it through `lpphy_set_tx_power_control()`, and writes mode bits back to hardware.
- `tx_isolation_*`, `max_tx_pwr_*`, `tx_max_rate*`, `txpa*`, `rx_pwr_offset`, `rssi_*`, and `bx_arch` are populated from `struct ssb_sprom` by band. They drive baseband init, RSSI setup, transmit isolation compensation, and power limits.
- `tssi_tx_count`, `tssi_idx`, `tssi_npt`, `tgt_tx_freq`, and `tx_pwr_idx_over` support TSSI/TX power-control sequencing. Several comments mark initial values and update paths as FIXME/TODO, which is an important maturity signal.
- `rc_cap` stores RC calibration results and is later pushed back into 2062 radio registers via `lpphy_set_rc_cap()`.
- `dig_flt_state[9]` saves/restores selected digital filter registers around calibration, notably in baseband and full-calibration paths.
- `crs_usr_disable` and `crs_sys_disable` track two independent CRS disable reasons so user and internal calibration suppression do not accidentally re-enable carrier sense while another owner still needs it disabled.
- `channel`, `antenna`, and `tx_tone_freq` cache runtime hardware selection/tone state for restoration after calibration and RF operations.
- `full_calib_chan`, `tx_iqloc_best_coeffs_valid`, and `tx_iqloc_best_coeffs` record calibration-specific state across LP calibration routines.

The state is reset by `prepare_structs()` and therefore must be repopulated before use. The source contains FIXME notes for array sizes and initial values, indicating that some LP PHY calibration contracts are inferred from reverse-engineered behavior rather than a fully documented hardware specification.

## Dependencies

This header depends on b43 core definitions supplied before or alongside it:

- `B43_PHY_CCK()` and `B43_PHY_OFDM()` encode PHY register windows and come from b43 PHY/core headers.
- `struct b43_phy_operations` is forward-declared here and fully defined in `phy_common.h`.
- `struct b43_phy_lp` is forward-declared in `phy_common.h` and stored in the LP member of the `struct b43_phy` union.
- `enum b43_lpphy_txpctl_mode` is used only by LP implementation code and must remain consistent with hardware mode bit constants in this same header.
- LP table access in `tables_lpphy.c` and `tables_lpphy.h` uses the radio/PHY register constants from this file for table initialization and radio register upload.
- The implementation uses Linux kernel facilities such as `u8`, `u16`, `s8`, `s16`, `bool`, `kzalloc`, and b43 MMIO/PHY/radio accessors.

Build integration is controlled by the b43 Makefile line that includes `phy_lp.o` under `CONFIG_B43_PHY_LP`. At runtime, LP PHY support is selected only for devices whose detected `phy->type` is `B43_PHYTYPE_LP`.

## Integration Points

Primary integration points are:

- `phy_lp.c`, which includes this header and consumes nearly all register definitions and `struct b43_phy_lp`.
- `tables_lpphy.c`, which includes this header to upload 2062/2063 radio init tables and write LP gain/TX power tables.
- `phy_common.c`, which includes this header to install `b43_phyops_lp` for LP PHY devices.
- `phy_common.h`, which forward-declares `struct b43_phy_lp` and stores it in the active PHY union.
- `main.c` and `xmit.c`, which branch on `B43_PHYTYPE_LP` for channel, band, transmit header, and PHY-specific behavior through the common operations layer rather than by using this header directly.

The header is part of a larger driver split where common code dispatches via `struct b43_phy_operations`, while the LP implementation uses these constants to operate the hardware directly. It is therefore both a compile-time interface and a reverse-engineered hardware map.

## Risks and Edge Cases

- Register constants are raw hardware contracts. A wrong offset, north/south bank decoration, or mode mask can silently program the wrong RF/PHY block, causing radio malfunction rather than a normal software failure.
- The header exposes many unknown or FIXME-marked areas: `B43_LPPHY_4C3` to `_4C5` are marked unknown, `tx_max_rate*` array sizing is questioned, and several state fields have FIXME initial-value comments. These are maintenance risks for new hardware revisions.
- `struct b43_phy_lp` is heavily coupled to calibration order. Code that uses fields before SPROM load, after `prepare_structs()` reset, or after failed channel/radio initialization can propagate zero/default calibration data into hardware.
- The TX power-control mode exists both in hardware bits and cached driver state. Desynchronization between `txpctl_mode` and `B43_LPPHY_TX_PWR_CTL_CMD` can leave software believing power control is disabled, software-controlled, or hardware-controlled when the radio is doing something else.
- Several TX power paths in `phy_lp.c` are TODO or stubbed (`adjust_txpower`, `recalc_txpower`, parts of hardware mode setup). The state definitions in this header therefore describe an intended contract that is only partially implemented.
- Channel and calibration routines write many AFE/RF override registers. Failure to restore `dig_flt_state`, CRS flags, gain overrides, antenna selection, or channel state can degrade receive sensitivity, break transmit power, or leave carrier sense disabled.
- LP PHY support is explicitly SSB-only in the implementation. If the header is reused without preserving that guard, PCIe/BCMA-style devices could enter unsupported register flows.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Kernel build coverage with `CONFIG_B43_PHY_LP=y` or `m`, because the header is mostly compile-time symbol contract and missing/renamed registers surface as compile failures in `phy_lp.c` and `tables_lpphy.c`.
- Boot/probe logs on LP-PHY hardware should show successful PHY allocation and no `LP-PHY is supported only on SSB!` error for supported SSB devices.
- Channel-switch testing should verify both 2.4 GHz and 5 GHz paths where hardware supports them, with `B43_MMIO_CHANNEL` and cached `lpphy->channel` following requested channel changes.
- Calibration smoke tests should look for successful RC calibration, full calibration on channel changes, restored analog/filter state, and no persistent CRS disable after calibration.
- TX power-control testing should exercise off/software/hardware modes and inspect `B43_LPPHY_TX_PWR_CTL_CMD` mode bits alongside `lpphy->txpctl_mode`.
- RF kill and analog switch testing should confirm `B43_LPPHY_AFE_CTL_OVR`/`OVRVAL` behavior does not leave the analog front end disabled after unkill/resume.
- Runtime wireless tests should include association, scan, RX sensitivity, TX throughput, and rate behavior after suspend/resume or repeated channel switches, because most failures here would result from incorrect cached LP PHY state or register restore ordering rather than obvious crashes.

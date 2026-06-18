# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp_hw.h

## Purpose

`ice_ptp_hw.h` is the public and private contract for the `ice` PTP hardware layer. It declares timer command enums, link-speed/FEC enums, calibration data structures, DPLL/CGU pin descriptors, exported PTP hardware APIs, inline E82x time-reference helpers, family-specific APIs, and a large set of register offsets and bit masks used by `ice_ptp_hw.c`.

## Important APIs, Types, And Constants

`enum ice_ptp_tmr_cmd` defines the abstract timer commands consumed by the C file: init time, init incval, adjust time, adjust-at-time, read time, and no-op. `enum ice_ptp_serdes`, `enum ice_ptp_link_spd`, `enum ice_ptp_fec_mode`, and `enum ice_eth56g_link_spd` normalize hardware link encodings for calibration logic.

`struct ice_time_ref_info_e82x` maps E82x TIME_REF choices to PLL frequency and nominal incval. `struct ice_vernier_info_e82x` stores E82x Vernier calibration frequencies and fixed delays. `struct ice_eth56g_mac_reg_cfg` stores ETH56G MAC TSU mode, delay, fixed-point offset, and one-step/SFD parameters. `struct ice_cgu_pin_desc` backs DPLL pin discovery.

The header declares the common API used outside the hardware file: `ice_ptp_init_hw`, `ice_ptp_init_phc`, `ice_ptp_init_time`, `ice_ptp_write_incval`, `ice_ptp_write_incval_locked`, `ice_ptp_adj_clock`, timestamp read/clear/readiness helpers, and CGU/SMA helpers. It also declares E82x and ETH56G family functions needed by other driver modules.

The register section defines source timer command bits (`GLTSYN_CMD_*`), PHY command bits (`PHY_CMD_*`), sync command values, E82x quad/port register offsets, E810/E830 GLTSYN offsets, low-latency proxy fields, timestamp-bank address macros, SMA GPIO masks, and ETH56G PHY/MAC/quad register offsets.

## Control Flow Role

The header does not execute control flow, but it encodes the control decisions used by `ice_ptp_hw.c`. `ice_get_base_incval` selects a nominal source increment value based on `hw->mac_type`. Inline E82x helpers get and set `hw->func_caps.ts_func_info.time_ref`, and derive PLL frequency/incval from exported calibration tables.

Register macros keep the C file from hard-coding family-specific offsets. For example, E82x timestamp memory uses `Q_REG_TX_MEMORY_*` and `TS_L`/`TS_H`, E810 external PHY access uses `TS_EXT`, and ETH56G resource spaces use `PHY_*` offsets and one-step PTP masks.

## State And Persistence Behavior

The header itself has no runtime state. Its types describe state stored elsewhere: `hw->ptp`, PHY calibration tables, DPLL pin descriptors, and hardware register fields. The `extern` calibration tables must remain consistent with the enum ordering in this header, especially `NUM_ICE_PTP_LNK_SPD`, `NUM_ICE_ETH56G_LNK_SPD`, and `NUM_ETH56G_PHY_RES`.

## Dependencies And Integration Points

The header includes `<linux/dpll.h>` for DPLL pin types, frequencies, lock status, and pin capability bits. It is included by PTP implementation files, common device code, TSPLL code, and other modules that need hardware-level PTP operations. It relies on register helper macros from the broader `ice` driver, such as `BIT`, `GENMASK`, `FIELD_PREP`, `ICE_M`, and hardware register names declared in other generated or shared headers.

## Risks And Edge Cases

Enum ordering is part of the ABI between tables and code. Adding a link speed, resource type, or TIME_REF without updating tables can silently index the wrong calibration constants. Masks for 40-bit and 64-bit timestamp layouts differ by family; using `PHY_EXT_40B_*` where `PHY_40B_*` is expected, or vice versa, will corrupt timestamps. Duplicate C827 handle defines are present and should remain consistent if edited.

## Test Signals

Compile coverage is the first signal: all prototypes must match `ice_ptp_hw.c`, and all macros must resolve against the target kernel tree. Runtime signals include correct base incval selection for E810/E830/E82x/E825, successful DPLL pin enumeration, and timestamp values whose high/low parts match the expected family layout.

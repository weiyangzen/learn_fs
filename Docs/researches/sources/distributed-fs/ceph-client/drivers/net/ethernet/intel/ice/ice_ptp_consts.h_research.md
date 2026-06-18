# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp_consts.h

## Purpose

`ice_ptp_consts.h` contains constant lookup tables used by ICE PTP hardware support. The tables describe ETH56G PHY register resource address layouts, speed/FEC-specific ETH56G MAC timestamp configuration values, E82X time-reference PLL frequencies and nominal increment values, and E822 Vernier calibration clock/fixed-delay constants.

The file is data-only: it has no functions and no direct control flow. Its values are consumed by `ice_ptp_hw.c` through declarations in `ice_ptp_hw.h` to program PHC frequency, PHY/MAC timestamp offsets, clock conversion registers, and fixed Tx/Rx timestamp delay corrections.

## Important APIs, Types, And Functions

- `eth56g_phy_res[NUM_ETH56G_PHY_RES]` maps ETH56G PTP, XPCS, MAC, and GPCS resource classes to base addresses and per-port/per-lane register strides.
- `eth56g_mac_cfg[NUM_ICE_ETH56G_LNK_SPD]` provides per-link-speed MAC timestamp configuration for ETH56G/E825C-class hardware, including Tx/Rx mode selectors, marker/codeword delays, block timing, marker timing, and Tx/Rx offset components for SerDes, no-FEC, FireCode FEC, Reed-Solomon FEC, SFD, bitslip/deskew, and one-step timestamping.
- `e82x_time_ref[NUM_ICE_TSPLL_FREQ]` maps supported E82X TSPLL reference frequencies to PLL output frequency and nominal PHC increment value.
- `e822_vernier[NUM_ICE_PTP_LNK_SPD]` maps E822 link-speed/FEC modes to Tx/Rx PAR and PCS clock frequencies, deskew/RS gearbox clocks, fixed Tx/Rx delays, and PMD adjustment divisors.

There are no callable functions. The exported objects are `const` arrays whose types are defined in `ice_ptp_hw.h`.

## Control Flow

Runtime code indexes these tables after determining hardware family, link speed, FEC mode, or TSPLL time-reference capability. ETH56G code uses `eth56g_phy_res` to derive register addresses and `eth56g_mac_cfg` to select mode and offset programming for the active link speed. E82X code uses `e82x_time_ref` to compute PLL frequency and nominal increment values, and E822 Vernier code uses `e822_vernier` to program conversion ratios and calculate fixed Tx/Rx offset adjustments.

Unused fields are encoded as zero in several entries. Consumer code treats zero clock fields as "clear or skip this register" for link modes where a PAR/PCS/deskew clock is not applicable. Speed entries distinguish non-FEC, FireCode, Reed-Solomon, one-step, SFD, and bitslip/deskew offsets so higher-level hardware helpers can compose the correct delay correction.

## State And Persistence

The file defines immutable in-kernel data. It stores no runtime state, takes no locks, and performs no persistence. Its values influence persistent hardware register state only when caller code writes derived values into PHY, MAC, TSPLL, or PHC registers.

Because the arrays are indexed by enums and compile-time counts, their correctness depends on keeping initializer indices aligned with `NUM_ETH56G_PHY_RES`, `NUM_ICE_ETH56G_LNK_SPD`, `NUM_ICE_TSPLL_FREQ`, and `NUM_ICE_PTP_LNK_SPD`. A wrong constant persists indirectly as systematic timestamp offset, frequency, or calibration error at runtime.

## Dependencies And Integration Points

The table element types and enum indexes come from `ice_ptp_hw.h`, which declares these arrays as externs. `ice_ptp_hw.c` is the primary consumer: it uses `eth56g_mac_cfg` for ETH56G MAC timestamp programming, `e82x_time_ref` through inline helpers such as PLL frequency and nominal increment lookup, and `e822_vernier` for E822 Vernier conversion and delay calculations.

The constants integrate with the high-level PTP lifecycle in `ice_ptp.c` indirectly. During PHC initialization, frequency adjustment, link-change recalibration, PHY start/restart, and reset rebuild, `ice_ptp.c` calls hardware helpers that rely on these tables to program the correct family-specific values.

## Risks

- The data is hardware-calibration sensitive. A single wrong offset, clock frequency, or divisor can create consistent nanosecond-scale or larger timestamp error that normal build tests will not catch.
- Enum/table drift is a major risk. If a new link speed, FEC mode, time reference, or resource enum is added without a matching indexed initializer, code may read zeroed values or the wrong speed entry.
- Some comments show human-readable fractional timing interpretations. They are helpful but not mechanically checked; stale comments can mislead later calibration edits.
- Zero has semantic meaning for unused clock fields. Consumer code must continue distinguishing intentional zero from missing data.
- The arrays are defined in a header rather than a C file. This is safe only if the build includes it in exactly the intended translation unit or with compatible linkage assumptions; otherwise duplicate definitions would be possible.

## Test Signals

Useful validation includes compile-time checks that array sizes match enum counts, hardware timestamp accuracy tests per supported ETH56G link speed and FEC mode, E82X PHC frequency drift tests for each supported time reference, E822 Vernier Tx/Rx calibration tests across 1G/10G/25G/25G-RS/40G/50G/50G-RS/100G-RS, and regression tests comparing programmed register values against hardware specification tables. Static review should verify every indexed enum has an explicit initializer and that consumer code handles zero-valued unused fields intentionally.

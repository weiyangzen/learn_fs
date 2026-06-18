# Research: subset-b-004806

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.c

## Purpose

`phy_qmath.c` implements the small fixed-point arithmetic helper layer used by Broadcom `brcmsmac` PHY calibration code. It provides saturated 16-bit and 32-bit arithmetic, signed and unsigned fixed-point multiplication, normalization, bidirectional shifts, and a table/interpolation based `log10()` routine that avoids floating point in kernel/driver code. The file has no device state of its own; its purpose is deterministic math support for PHY calculations such as transmit gain estimation in `phy_lcn.c`.

## Important APIs, Types, And Functions

- `qm_mulu16(u16 op1, u16 op2)` multiplies two unsigned 16-bit fixed-point values and returns the high 16 bits of the 32-bit product.
- `qm_muls16(s16 op1, s16 op2)` multiplies signed 16-bit values and returns a Q15-style result, with a special saturation branch for `0x8000 * 0x8000`.
- `qm_add32()`, `qm_add16()`, and `qm_sub16()` perform saturating arithmetic. `qm_add32()` detects signed overflow from the wrapped result; the 16-bit helpers compute in `s32` and clamp to `0x7fff` or `0x8000`.
- `qm_shl32()` and `qm_shl16()` implement saturated left shift by repeated saturated doubling, and arithmetic right shift for negative shifts. `qm_shr16()` is a thin inverse wrapper around `qm_shl16()`.
- `qm_norm32()` counts redundant sign bits in a 32-bit signed value and is used to normalize magnitudes before lookup/interpolation.
- `qm_log10(s32 N, s16 qN, s16 *log10N, s16 *qLog10N)` computes a fixed-point base-10 logarithm using `log_table[]`, interpolation, and multiplication by `LOG10_2`.

## Control Flow

Most helpers are straight-line arithmetic with clamp checks. The shift helpers clamp requested shift ranges to `[-31, 31]` for 32-bit and `[-15, 15]` for 16-bit, then use repeated saturated addition for positive left shifts. `qm_log10()` is the only multi-stage algorithm: it normalizes `N`, adjusts `qN`, derives a five-bit table index from the normalized mantissa, takes a 16-bit interpolation offset, adds the exponent contribution, normalizes the log2 result, converts it to log10 by multiplying with `LOG10_2`, and returns both value and resulting Q format.

## State And Persistence

There is no mutable state, heap allocation, I/O, or persistence. The only private data is the compile-time `log_table[]`. All exported functions are pure for valid pointer arguments, except that `qm_log10()` writes through `log10N` and `qLog10N`.

## Dependencies And Integration Points

The implementation includes only `phy_qmath.h`, which pulls in Broadcom/Linux integer aliases from `<types.h>`. `phy_lcn.c` calls `qm_log10()`, `qm_shr16()`, and `qm_sub16()` while computing gain-related quantities from LCN PHY table entries. These helpers are expected to be link-visible within the brcmsmac PHY object set through prototypes in `phy_qmath.h`.

## Risks And Edge Cases

- `qm_log10()` does not guard `N <= 0`; `N == 0` leads to `qm_norm32(0) == 31`, then left-shifts zero and indexes `log_table[0]`, but a mathematical log of zero is undefined. Negative input normalization/table lookup also relies on signed shifts and is not a meaningful logarithm path.
- `qm_norm32()` left-shifts signed values in its loop. Kernel toolchains generally tolerate this legacy driver pattern, but strictly speaking signed overflow/left-shift behavior can be compiler-sensitive.
- Saturation constants are written as hex literals cast to signed types. The intended values are clear, but changes to type widths or warning policy could expose implementation-defined conversions.
- `qm_shl32()` and `qm_shl16()` use loops rather than one-step shift and saturation, so unusually large repeated calls in hot paths would be slower, though shift counts are bounded.

## Test Signals

Useful checks are focused unit vectors: signed multiply saturation for `0x8000 * 0x8000`, add/sub overflow clamps, positive and negative shift boundaries, `qm_norm32()` examples, and `qm_log10()` comparisons for known fixed-point powers. Integration signals are successful brcmsmac build, LCN PHY initialization without calibration regressions, and stable transmit-gain behavior on hardware paths that call `phy_lcn.c` math.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.h

## Purpose

`phy_qmath.h` is the public declaration header for the brcmsmac PHY fixed-point math helpers implemented in `phy_qmath.c`. It gives the PHY implementation files a compact, floating-point-free arithmetic API for calibration and gain computations.

## Important APIs, Types, And Functions

The header includes `<types.h>` and declares the fixed-width integer based API: `qm_mulu16()`, `qm_muls16()`, `qm_add32()`, `qm_add16()`, `qm_sub16()`, `qm_shl32()`, `qm_shl16()`, `qm_shr16()`, `qm_norm32()`, and `qm_log10()`. The API uses `u16`, `s16`, and `s32`; `qm_log10()` returns two values by pointer, the computed logarithm and its Q-format exponent.

## Control Flow

The header has no runtime control flow. Its compile-time control flow is a normal include guard `_BRCM_QMATH_H_`, followed by type inclusion and prototypes.

## State And Persistence

No state is declared. The header exposes functions only and does not define storage, inline functions, or macros that mutate caller state.

## Dependencies And Integration Points

It depends on Broadcom/Linux `types.h` aliases and is included by `phy_qmath.c` and PHY code that needs fixed-point helpers. `phy_lcn.c` uses this interface for gain-table derived calculations, so this header is part of the internal ABI between the qmath implementation and PHY calibration code.

## Risks And Edge Cases

- The header documents no valid input ranges; callers must know fixed-point Q formats and avoid invalid `qm_log10()` arguments.
- The API has no `const` or nullability annotations for `qm_log10()` output pointers, so misuse is caught only by runtime failure or static analysis outside this header.
- Because these are external declarations, any signature drift from `phy_qmath.c` would be a build/link failure.

## Test Signals

Compile coverage is the main header-level signal: all users should build cleanly with the prototypes. Functional tests belong to `phy_qmath.c`, especially vectors around saturation, normalization, and Q-format return values from `qm_log10()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_radio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_radio.h

## Purpose

`phy_radio.h` is a hardware register map header for Broadcom radio cores used by the brcmsmac PHY layer. It names radio register offsets, read-offset encodings, core-selection constants, power/RSSI/calibration bit masks, and per-core 2055/2056/2057 register addresses. It lets PHY calibration and channel code use symbolic names when programming RF analog blocks.

## Important APIs, Types, And Functions

The file defines no functions or types. Its important symbols are macro families:

- Common symbols such as `RADIO_IDCODE`, `RADIO_DEFAULT_CORE`, RSSI/TSSI control bits, and read-offset constants like `RADIO_2055_READ_OFF`, `RADIO_2057_READ_OFF`, and `RADIO_2064_READ_OFF`.
- `RADIO_2055_*` register offsets and masks for PLL, VCO, LGEN, RX/TX, RSSI, calibration, core1/core2 gain, and gain-boost controls.
- `RADIO_MIMO_CORESEL_*` values for selecting one or more MIMO RF cores.
- `RADIO_2064_REG000` through `RADIO_2064_REG130`, a dense numeric map for the 2064 radio.
- `RADIO_2056_*` block selectors (`SYN`, `TX0`, `TX1`, `RX0`, `RX1`, `ALLTX`, `ALLRX`) and synth/TX/RX local register offsets plus power-up and RSSI selection masks.
- `RADIO_2057_*` and `RADIO_2057v7_*` offsets for shared, core0, core1, TX IQ/TSSI, AFE, RCCAL, override, and revision-specific registers.

## Control Flow

There is no runtime control flow. Compile-time structure is an include guard `_BRCM_PHY_RADIO_H_` around a large list of constants. Higher-level PHY code combines these addresses with radio read/write helpers and revision checks.

## State And Persistence

The header defines symbolic constants only. It does not store hardware state, but its values address persistent radio hardware registers. Writes through users of these macros can affect RF power-up, calibration, gain, RSSI, TSSI, PLL, and transmit/receive behavior until hardware reset or reprogramming.

## Dependencies And Integration Points

This header integrates with N-PHY and LCN-PHY code that performs low-level radio register reads and writes through brcmsmac PHY helper functions. The constants are consumed by calibration, channel switching, RSSI, TSSI, power control, and RF-sequence logic. It is coupled to actual Broadcom silicon register layouts for 2055, 2056, 2057, and 2064 radio families.

## Risks And Edge Cases

- A wrong numeric constant can silently program the wrong analog register, causing radio failure, poor sensitivity, bad transmit power, or regulatory issues.
- Several radio families and revisions share similarly named registers with different address composition rules; users must combine block selectors and offsets correctly.
- The header provides masks and shifts but no type safety, so accidental use with the wrong radio family is a compile-clean runtime bug.
- Because register effects are hardware-dependent, many changes cannot be validated by ordinary unit tests.

## Test Signals

The best validation is compile coverage plus hardware bring-up: successful attach, channel set, RF calibration completion, stable RSSI/TSSI readings, expected transmit power, and no PHY watchdog/calibration errors. Static review should compare changed addresses against vendor register specs or known-good upstream history.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_radio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phyreg_n.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phyreg_n.h

## Purpose

`phyreg_n.h` defines N-PHY table IDs, register bit masks, RF sequence command values, classifier/IQ/sample-control bits, and small register-address selector macros. It is the symbolic bridge between N-PHY control code and the numeric PHY table/register layout.

## Important APIs, Types, And Functions

There are no functions or types. Important macro groups include:

- `NPHY_TBL_ID_*` constants for gain, RF sequence, AFECTRL, antenna switch, IQ local, noise variance, sample play, per-core TX power-control, and PAPD epsilon/scalar tables.
- Band and RF-control masks such as `NPHY_BandControl_currentBand`, `RFCC_CHIP0_PU`, `RFCC_POR_FORCE`, `RIFS_ENABLE`, `BPHY_BAND_SEL_UP20`, and `NPHY_MLenable`.
- RF sequence mode, trigger, status, operation index, and command constants for pre-rev3 and rev3 hardware.
- Classifier, IQ flip, sample command, IQ estimation, TX power index, RSSI selector, rail selector, and rev7 RF-control override/gain-code masks.
- `NPHY_Iqest*Acc*()` macros that choose per-core IQ estimator accumulator register addresses.

## Control Flow

The file has no runtime control flow and no include guard. It is a macro-only header; control decisions happen in callers such as `phy_n.c`, which use the constants under PHY revision and core-selection branches.

## State And Persistence

No software state is declared. The constants identify hardware state fields and tables whose values are programmed by N-PHY initialization, calibration, gain control, IQ estimation, and power-control routines.

## Dependencies And Integration Points

`phytbl_n.c` table descriptors use compatible table IDs, and `phy_n.c` writes those tables with `wlc_phy_write_table_nphy()`. The RF sequence and override constants are consumed by N-PHY state-machine setup and calibration paths. The per-core accumulator macros are used when collecting IQ/power estimates for a selected receive/transmit chain.

## Risks And Edge Cases

- No include guard means repeated inclusion is normally harmless for identical macros but still relies on consistent definitions and compiler tolerance for redefinitions.
- Table ID mismatches with `phytbl_n.c` descriptors would load valid data into the wrong hardware table.
- Pre-rev3 and rev3 RF sequence command values differ; using the wrong macro family can corrupt the RF transition program.
- The per-core address macros assume only core `0` and nonzero/other core; callers must not pass arbitrary indexes expecting more than two distinct address sets.

## Test Signals

Compile `phy_n.c` users, then validate N-PHY initialization on rev0, rev3, rev7, and rev16 hardware paths if available. Runtime signals include successful table programming, RF sequence completion, IQ estimate collection, gain updates, and absence of PHY calibration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phyreg_n.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.c

## Purpose

`phytbl_lcn.c` is the LCN-PHY static table bank. It contains immutable numeric tables for receive gain, auxiliary gain indexes, gain values, noise-floor and noise-scale data, filter/power-save control, switch-control variants, spur suppression, unsupported MCS entries, IQ-local data, PAPD compensation deltas, and 128-entry transmit-gain tables for 2.4 GHz, 2.4 GHz external PA, and 5 GHz operation. It exports `struct phytbl_info` descriptors that tell LCN PHY code which data pointer, length, PHY table ID, offset, and element width to write.

## Important APIs, Types, And Data

- RX gain descriptor arrays: `dot11lcnphytbl_rx_gain_info_rev0`, `dot11lcnphytbl_rx_gain_info_2G_rev2`, `dot11lcnphytbl_rx_gain_info_5G_rev2`, `dot11lcnphytbl_rx_gain_info_extlna_2G_rev2`, and `dot11lcnphytbl_rx_gain_info_extlna_5G_rev2`.
- Size exports: `dot11lcnphytbl_rx_gain_info_sz_rev0`, `dot11lcnphytbl_rx_gain_info_2G_rev2_sz`, and `dot11lcnphytbl_rx_gain_info_5G_rev2_sz`.
- Main default table descriptor array `dot11lcnphytbl_info_rev0`, which writes min-signal-square, noise scale, filter control, power-save control, gain index, auxiliary gain index, switch control, noise-floor, gain value, gain table, spur table, unsupported MCS, IQ-local, and PAPD compensation tables.
- Board/radio switch-control descriptors: `dot11lcn_sw_ctrl_tbl_info_4313`, `dot11lcn_sw_ctrl_tbl_info_4313_bt_ipa`, `dot11lcn_sw_ctrl_tbl_info_4313_epa`, `dot11lcn_sw_ctrl_tbl_info_4313_bt_epa`, and `dot11lcn_sw_ctrl_tbl_info_4313_bt_epa_p250`.
- TX gain arrays of `struct lcnphy_tx_gain_tbl_entry`: `dot11lcnphy_2GHz_extPA_gaintable_rev0`, `dot11lcnphy_2GHz_gaintable_rev0`, and `dot11lcnphy_5GHz_gaintable_rev0`.

## Control Flow

The file contains no executable functions. Its effective control flow is data-driven in `phy_lcn.c`: initialization iterates `dot11lcnphytbl_info_rev0`, selects RX gain arrays based on band and external-LNA configuration, selects a switch-control descriptor based on board flags such as BT coexistence, internal/external PA, and package variant, and writes TX gain entries through LCN table helpers.

## State And Persistence

All arrays are `static const` or exported `const`; there is no mutable state. Persistence is hardware-facing: once `phy_lcn.c` writes these descriptors to PHY tables, the programmed hardware tables persist until reset or later reinitialization. The data is firmware/driver calibration material and is not updated at runtime by this file.

## Dependencies And Integration Points

The file includes `<types.h>`, `phy_int.h` for `struct phytbl_info` and `ARRAY_SIZE`, and `phytbl_lcn.h` for exports. `phy_lcn.c` consumes the descriptors via `wlc_lcnphy_write_table()`/`wlc_lcnphy_read_table()` wrappers around common PHY table access. The TX gain arrays feed LCN transmit gain programming and downstream math that uses `phy_qmath.c` helpers.

## Risks And Edge Cases

- Table descriptor fields must match hardware table ID, offset, element width, and array length. A mismatch can silently corrupt LCN PHY tables.
- RX gain selection depends on band and external-LNA board data; incorrect descriptor selection affects sensitivity and gain control.
- The header declares `dot11lcn_sw_ctrl_tbl_info_4313_epa_combo`, but this source exports no matching definition in the inspected file. If any caller references that symbol, linking would fail; current observed LCN code uses the exported `bt_epa`/`bt_epa_p250`/`epa` variants instead.
- Static numeric tables have little self-documentation; accidental edits are hard to review without hardware reference data.
- The 5 GHz TX gain table uses sentinel-like high byte values (`255`) in gain fields, so consumers must interpret those entries exactly as existing code expects.

## Test Signals

Build/link coverage should confirm all declared/used symbols resolve. Runtime signals include LCN PHY table initialization loops completing, correct RX gain table chosen for 2G/5G and external-LNA boards, TX gain writes succeeding, stable receive sensitivity/noise floor, transmit power within expected range, and no calibration or association regressions on BCM4313/LCN hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.h

## Purpose

`phytbl_lcn.h` exposes the LCN-PHY table descriptors and transmit-gain table type/data defined in `phytbl_lcn.c`. It is the internal interface used by LCN PHY implementation code to load static calibration and control tables without depending on private array names.

## Important APIs, Types, And Data

- Extern declarations for default and RX-gain `struct phytbl_info` arrays and their size constants.
- Extern declarations for board-specific switch-control descriptors for BCM4313 variants.
- `struct lcnphy_tx_gain_tbl_entry` with `gm`, `pga`, `pad`, `dac`, and `bb_mult` byte fields, matching the TX gain tables consumed by LCN transmit gain programming.
- Extern declarations for `dot11lcnphy_2GHz_gaintable_rev0`, `dot11lcnphy_2GHz_extPA_gaintable_rev0`, and `dot11lcnphy_5GHz_gaintable_rev0`.

## Control Flow

The header has no runtime control flow. It also has no include guard, so repeated inclusion in the same translation unit would repeat the struct definition and extern declarations.

## State And Persistence

No mutable state is defined. All declared data is `const` storage in `phytbl_lcn.c`; consumers write referenced values into hardware PHY tables where they persist until reset or reprogramming.

## Dependencies And Integration Points

It includes `<types.h>` and `phy_int.h` for fixed-width types and `struct phytbl_info`. `phy_lcn.c` relies on this header during LCN PHY initialization, gain-table selection, switch-control table selection, and TX gain table loading.

## Risks And Edge Cases

- Missing include guard is a concrete maintenance hazard because this header defines `struct lcnphy_tx_gain_tbl_entry`; duplicate inclusion can produce a redefinition error.
- The declaration `dot11lcn_sw_ctrl_tbl_info_4313_epa_combo` has no matching definition in the inspected `phytbl_lcn.c`, making it a stale or incomplete API surface unless defined elsewhere.
- The split-line extern for `dot11lcnphy_2GHz_extPA_gaintable_rev0` is valid C but easy to disturb during mechanical edits.
- Callers must pair the correct size constants with the matching descriptor arrays; the header does not encode array lengths in types.

## Test Signals

Header validation is mostly build/link coverage: include it from LCN code, ensure no duplicate-include path hits the missing guard, and ensure all referenced externs resolve. Functional signals come from `phytbl_lcn.c` table loading on LCN hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.c

## Purpose

`phytbl_n.c` is the N-PHY/MIMO static table bank for brcmsmac. It stores large immutable tables for frame structure, frame lookup, tone maps, training, interleaving, pilots, TDI data for 20/40 MHz and antenna/core combinations, channel estimation, MCS, noise variance, estimated/adjusted power, gain control, IQ, LOFT, antenna switch control, and PAPD compensation/scalar data. It exports `struct phytbl_info` arrays grouped by N-PHY revision so `phy_n.c` can initialize hardware tables by iterating descriptors.

## Important APIs, Types, And Data

- Rev0 exports: `mimophytbl_info_rev0`, `mimophytbl_info_rev0_volatile`, and size constants. Rev0 splits baseline tables from volatile power/gain/IQ/LOFT tables.
- Rev3 exports: `mimophytbl_info_rev3`, four antenna-switch volatile variants (`mimophytbl_info_rev3_volatile*`), and size constants. Rev3 also exports `noise_var_tbl_rev3[]`.
- Rev7 exports: `mimophytbl_info_rev7`, `mimophytbl_info_sz_rev7`, and `noise_var_tbl_rev7[]`. Rev7 reuses many rev3 tables, changes tone/noise data, and adds PAPD epsilon/scalar tables.
- Rev16 exports: `mimophytbl_info_rev16` and size. This is a smaller descriptor set focused on noise/power/gain/IQ/LOFT tables reused from rev7/rev3 data.
- Many private `static const` arrays back those descriptor exports, including `frame_struct_rev0`, `frame_struct_rev3`, `tmap_tbl_rev0`, `tmap_tbl_rev3`, `tmap_tbl_rev7`, `tdtrn_tbl_*`, `mcs_tbl_*`, per-core TX power control tables, and PAPD tables.

## Control Flow

The file has no functions. Runtime behavior is driven by `phy_n.c`: N-PHY init chooses `mimophytbl_info_rev16`, `rev7`, `rev3`, or `rev0` based on PHY revision and writes each descriptor with `wlc_phy_write_table_nphy()`. Additional volatile writes are selected for rev3 antenna-switch control based on board flags, using `ANT_SWCTRL_TBL_REV3_IDX` from `phytbl_n.h` to substitute one of the variant arrays.

## State And Persistence

All data is immutable driver text/rodata. Hardware table state changes only when users write these descriptors into the device. Exported `noise_var_tbl_rev3` and `noise_var_tbl_rev7` are also read directly by calibration/noise code in `phy_n.c` to derive minimum noise variance values.

## Dependencies And Integration Points

The file includes `<types.h>`, `phy_int.h` for `struct phytbl_info`/`ARRAY_SIZE`, and `phytbl_n.h` for exported declarations. It is tightly coupled to `phyreg_n.h` table ID definitions and to `phy_n.c` initialization around lines that iterate `mimophytbl_info_sz_rev*` and program volatile arrays. Noise calibration paths in `phy_n.c` index `noise_var_tbl_rev3`/`rev7` directly, so those arrays are both table payloads and algorithm inputs.

## Risks And Edge Cases

- Descriptor metadata is as important as payload values. Wrong table ID, offset, width, or size can write a valid array into the wrong N-PHY table region.
- Revision reuse is subtle: rev7 and rev16 intentionally reuse rev3 arrays for several tables. A change meant for one revision can affect others.
- Volatile antenna switch tables for rev3 have four variants; wrong board selection can break antenna routing and RF performance.
- Direct `noise_var_tbl_*` indexing in `phy_n.c` assumes stable table lengths and positions. Truncating or reordering those arrays can break calibration without a compile error.
- The file is mostly numeric literals, so review requires comparison against known-good hardware tables rather than semantic code reasoning.

## Test Signals

Build coverage should ensure descriptor symbols and size constants match the header. Runtime validation includes successful N-PHY init for rev0/rev3/rev7/rev16 paths, table write completion, correct antenna-switch variant selection on supported boards, stable noise calibration using `noise_var_tbl_*`, and no regressions in receive sensitivity, MCS operation, transmit power control, PAPD, or channel changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.h

## Purpose

`phytbl_n.h` declares the N-PHY table descriptor arrays, descriptor counts, and exported noise-variance tables defined by `phytbl_n.c`. It is the internal interface between the static N-PHY table bank and the N-PHY initialization/calibration code.

## Important APIs, Types, And Data

- `ANT_SWCTRL_TBL_REV3_IDX` identifies the antenna-switch-control entry in the rev3 volatile descriptor sequence.
- Extern descriptor arrays and size constants for rev0, rev3, rev7, and rev16 N-PHY table initialization.
- Extern volatile descriptor arrays for rev0 and four rev3 antenna-switch variants.
- Extern `noise_var_tbl_rev3[]` and `noise_var_tbl_rev7[]`, which are used both as table payloads and direct calibration lookup data.

## Control Flow

There is no runtime control flow. The header has no include guard; it provides macros and extern declarations consumed by `phy_n.c`.

## State And Persistence

No state is defined in this header. It exposes `const` arrays owned by `phytbl_n.c`; callers persist their contents into hardware PHY tables during initialization and may read exported noise arrays for calculations.

## Dependencies And Integration Points

It includes `<types.h>` and `phy_int.h` for fixed-width types and `struct phytbl_info`. `phy_n.c` uses the declarations to select table banks by PHY revision, write volatile antenna-switch tables, and inspect noise-variance values during calibration.

## Risks And Edge Cases

- No include guard is a maintenance risk, though the current content is macro/extern-only and less fragile than a header with struct definitions.
- `ANT_SWCTRL_TBL_REV3_IDX` must stay aligned with the order of `mimophytbl_info_rev3_volatile`; if the array order changes, `phy_n.c` can patch/select the wrong descriptor.
- Size constants must match the corresponding arrays. The header cannot enforce pairing, so caller loops depend on correct definitions in `phytbl_n.c`.
- Direct noise table exports expose array layout assumptions to code outside the table bank.

## Test Signals

Compile/link all N-PHY users and exercise revision-specific initialization. Specific signals include correct descriptor loop counts, rev3 antenna switch variant writes, stable noise calibration reads from `noise_var_tbl_rev3`/`rev7`, and successful PHY attach/channel operation on hardware revisions covered by the arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.h -->

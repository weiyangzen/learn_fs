# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_0_0_sh_mask.h

## Purpose

`smu_7_0_0_sh_mask.h` is a generated AMD SMU 7.0.0 register bitfield header for the DRM AMD GPU driver tree. It exposes preprocessor constants for field masks and right-shift amounts used when packing, unpacking, and read-modify-writing SMU, clock, power-management, fuse, thermal, and dynamic-power-management registers. The file contains no executable code; its behavioral importance is that it is the ABI map between driver C code and hardware/firmware register layouts for the SMU 7.0.0 generation.

The header is protected by `SMU_7_0_0_SH_MASK_H` and contains 3,815 `#define` entries: 1,907 `*_MASK` macros and 1,907 matching `*__SHIFT` macros, plus the include guard. Most macros follow the generated convention:

- `<REGISTER>__<FIELD>_MASK`
- `<REGISTER>__<FIELD>__SHIFT`

This lets callers clear a field with the mask, place a value at `SHIFT`, or extract a field with `(reg & MASK) >> SHIFT`.

## Important APIs, Types, And Symbols

There are no C types, functions, inline helpers, or exported objects. The entire API surface is macro constants. Important macro families include:

- SMU indirect access and mailbox fields: `GCK_SMC_IND_INDEX`, `GCK_SMC_IND_DATA`, `SMC_IND_INDEX[_0..7]`, `SMC_IND_DATA[_0..7]`, `SMC_IND_ACCESS_CNTL`, `SMC_MESSAGE_[0..11]`, `SMC_RESP_[0..11]`, and `SMC_MSG_ARG_[0..11]`. These define address/data windows, auto-increment bits, mailbox message payloads, and response fields for communicating with the SMU.
- Clock and PLL control fields: `CG_DCLK_CNTL`, `CG_VCLK_CNTL`, `CG_ECLK_CNTL`, `CG_ACLK_CNTL`, `GCK_DFS_BYPASS_CNTL`, `CG_SPLL_FUNC_CNTL[_2..7]`, `SPLL_CNTL_MODE`, spread-spectrum fields, bypass clock selection, clock pin controls, PLL test controls, and display-gap/deep-sleep clock controls.
- Reset, boot, firmware, and fuses: `SMC_SYSCON_RESET_CNTL`, `SMC_SYSCON_CLOCK_CNTL_[0..2]`, `RCU_UC_EVENTS`, `RCU_MISC_CTRL`, `CC_RCU_FUSES`, `CC_SMU_MISC_FUSES`, `CC_SCLK_VID_FUSES`, `CC_*_FUSES`, `SMU_STATUS`, `SMU_FIRMWARE`, `SMU_INPUT_DATA`, `SMU_EFUSE_0`, and `PM_FUSES_[1..65]`.
- DPM table layout: `DPM_TABLE_[1..191]` describes firmware-visible power table words, including PID controller parameters, level counts, graphics DPM levels 0-7, ACPI level data, UVD/VCE/ACP/SAMU levels 0-7, boot levels, intervals, thresholds, and display CAC values.
- Soft-register table layout: `SOFT_REGISTERS_TABLE_[1..21]` covers reference clock, timer, feature and handshake toggles, display PHY config, activity metrics, enabled DPM level bitmaps, and reserved words.
- LCLK DPM controls: `SMU_LCLK_DPM_STATE_[0..7]_CNTL_[0..3]`, `SMU_LCLK_DPM_STATE_[0..7]_ACTIVITY_THRESHOLD`, `SMU_LCLK_DPM_LEVEL_COUNT`, `SMU_LCLK_DPM_CNTL`, `SMU_LCLK_DPM_CURRENT_AND_TARGET_STATE`, and thermal-throttling thresholds.
- Runtime feature/status and power controls: `FEATURE_STATUS`, `PM_CONFIG`, `PM_INTERVAL_CNTL_[0..2]`, `PKG_PWR_CNTL`, `PKG_PWR_STATUS`, `PDM_STATUS`, `PDM_CNTL_[1..3]`, BAPM status/parameters, SVI telemetry, voltage/current overrides, AVS/AVSNB controls, HTC controls, and package/GPU power fields.
- Thermal and telemetry fields: `TEMPERATURE_READ_ADDR`, `CURRENT_GNB_TEMP`, `CURRENT_GLOBAL_TEMP`, `TE[0..2]_TEMPERATURE_READ_ADDR`, `AVS_*_TEMPERATURE_SENSOR`, `CG_THERMAL_INT_ENA`, `CG_THERMAL_INT_CTRL`, `CG_THERMAL_INT_STATUS`, and entity/power readbacks.
- Frequency-transition and deep-sleep voting: `SCLK_PWRMGT_CNTL`, `TARGET_AND_CURRENT_PROFILE_INDEX[_1]`, `CG_FREQ_TRAN_VOTING_[0..7]`, `SCLK_DEEP_SLEEP_CNTL[_2..3]`, `LCLK_DEEP_SLEEP_CNTL[_2]`, and related activity/busy mask fields.
- External byte APIs and debug/status windows: `EXT_API_IN_DATA_0_[0..3]`, `EXT_API_OUT_DATA_0_[0..3]`, `SMU_MONITOR_PORT80_*`, `SMU_PM_STATUS_[0..127]`, and LCAC control/override blocks.

## Control Flow

The header has no runtime control flow. At compile time, inclusion makes the constants visible to C compilation units. Runtime control flow exists in callers that read MMIO/SMC registers, clear bits with `*_MASK`, shift values with `*__SHIFT`, then write the resulting word back to hardware or firmware-owned tables.

Typical caller patterns are:

1. Read a 32-bit register or table word from MMIO, an indirect SMC window, or an SMU firmware table.
2. Clear a field using `word &= ~FIELD_MASK`.
3. Insert a new value using `word |= value << FIELD__SHIFT`, normally relying on the value already fitting the field width.
4. Write the modified word back, or extract state with `(word & FIELD_MASK) >> FIELD__SHIFT`.

The file's repeated table definitions encode structural control assumptions used elsewhere: eight graphics DPM levels, eight UVD/VCE/ACP/SAMU levels, eight LCLK DPM states, multiple SMC mailbox slots, and 128 SMU PM status words.

## State And Persistence Behavior

The header itself stores no state and performs no persistence. Its constants describe hardware, firmware, and fuse-backed state:

- Volatile hardware state: clock dividers, PLL reset/power/bypass bits, DPM current/target indexes, thermal interrupt status, package power status, and PM status windows.
- Firmware-owned state: SMU message/response registers, firmware boot/read status fields, DPM and soft-register tables, external API byte buffers, and feature status flags.
- Persistent or semi-persistent hardware configuration: eFuse and PM fuse fields such as disable bits, VID tables, leakage/power limits, core disable fields, LPML/GNB limits, and clock divider IDs.

Incorrect constants can therefore cause persistent hardware capability data to be misread or volatile power/clock state to be programmed incorrectly, even though this file does not itself write hardware.

## Dependencies

This file has no `#include` dependencies. It depends externally on the generated AMD ASIC register documentation matching SMU 7.0.0 hardware. It is normally paired with corresponding register offset headers, especially `smu_7_0_0_d.h`, so a caller can combine `mm<REGISTER>` addresses with the mask/shift constants here.

The exact in-tree direct include users found for this header are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_smc.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_dpm.c`

Related AMD power-management files use equivalent macro names from sibling ASIC headers, so this file participates in a broader generated-header pattern across SMU revisions.

## Integration Points

The main integration point is the AMDGPU legacy DPM path for Kaveri-era SMU hardware. `kv_smc.c` and `kv_dpm.c` include this header to build and interpret SMU power-management transactions. The constants support:

- SMU firmware boot and mailbox handshakes.
- DPM table construction for graphics, UVD, VCE, ACP, SAMU, GIO/LCLK, ACPI, and boot levels.
- Clock and PLL setup, including SPLL, D/V/E/A clock divider controls, bypass routing, spread spectrum, and deep-sleep dividers.
- Power and thermal policy programming through BAPM, HTC, TDC, package power, PDM, AVS, SPMI, and thermal interrupt fields.
- Runtime feature detection through `FEATURE_STATUS` and current/target index fields.
- Indirect register access through SMC index/data windows.

Because these are macro constants, integration errors are compile-time silent when a wrong but defined macro is used. Most semantic validation happens only through hardware behavior.

## Risks

- Generated-header drift: if the masks/shifts do not match the SMU 7.0.0 register spec or firmware table layout, callers will write the wrong bits with no type-system protection.
- Cross-ASIC confusion: sibling headers such as `smu_7_0_1_sh_mask.h` share many macro names but can assign different masks or shifts. Accidentally mixing register offsets from one ASIC revision with masks from another can corrupt programming sequences.
- Field-width truncation: the macros provide masks and shifts but no helper that bounds input values. Callers must mask or validate values before shifting them into fields.
- Reserved-bit writes: many registers include reserved fields. Read-modify-write paths need to preserve reserved bits unless the hardware programming guide requires a specific value.
- Full-word fields hide semantics: numerous fields use `0xffffffff` with shift `0`, especially table words and PM status windows. These are easy to pass through but provide no local documentation of scaling, signedness, units, or firmware ownership.
- Hardware sequencing risk: PLL reset, power, bypass, clock gating, DPM enable, thermal throttle, and fuse interpretation bits are sequencing-sensitive. The header cannot enforce required delays, polling, or ordering.
- Name collisions: these macro names are not namespaced by C scope. Including multiple ASIC mask headers with overlapping register names in one translation unit can cause redefinition conflicts or accidental use of the wrong definition.

## Test Signals

Useful signals for validating this file are mostly compile-time and hardware/driver behavior tests:

- Build coverage for AMDGPU legacy DPM users, especially `kv_smc.c` and `kv_dpm.c`, with this header included.
- Preprocessor or static checks that each field has both a `*_MASK` and matching `*__SHIFT` macro; this file currently has balanced counts of 1,907 mask and 1,907 shift macros.
- Register-layout comparison against the authoritative SMU 7.0.0 generated source or hardware XML/register database.
- Runtime smoke tests on matching hardware: SMU firmware loads, mailbox commands receive expected responses, DPM tables upload successfully, and graphics/UVD/VCE/ACP/SAMU levels enumerate correctly.
- Power-management functional tests: SCLK/LCLK DPM transitions, deep-sleep entry/exit, thermal interrupt thresholds, package power limits, BAPM/TDC/HTC behavior, and suspend/resume/ACPI state transitions.
- Negative/debug signals: no SMU timeouts, no repeated firmware NACKs, no unexpected thermal throttling, no incorrect feature status bits, no DPM level count mismatches, and no register readback differences after read-modify-write sequences.

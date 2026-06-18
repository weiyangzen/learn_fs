# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_0_sh_mask.h lines 1-4583

## Scope And Purpose

This chunk is the first 4,583 lines of the AMDGPU SMU 7.1.0 register field mask header. It begins with the AMD register-documentation license and the `SMU_7_1_0_SH_MASK_H` include guard, then defines mask and shift macros for SMU, clock, fuse, DPM, thermal, fan, memory-controller, and power-management fields.

The file is generated-style hardware description, not executable logic. Its purpose is to give C code stable symbolic names for extracting and composing bitfields in 32-bit MMIO or SMC table words. Each field is represented by paired macros using the pattern `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`. In this chunk there are 4,558 `#define` lines, and the assigned range ends in the middle of the `GENERAL_PWRMGT` field list at `GENERAL_PWRMGT__GPU_COUNTER_ACPI_MASK`.

## Register Families Covered

The opening section covers direct SMU/GCK and clock-generator controls: indirect SMC index/data registers, `CG_*CLK_CNTL` divider and direction-control fields for DCLK/VCLK/ECLK/ACLK, DFS bypass bits, SPLL configuration, spread-spectrum controls, clock pin controls, PLL test controls, and ADFS bypass selectors. These macros are low-level clock tree and PLL programming primitives.

The next hardware-control block covers SMC indirect windows and message channels. It includes `SMC_IND_INDEX`/`SMC_IND_DATA` plus numbered 0-7 windows, `SMC_IND_ACCESS_CNTL` auto-increment enables, `SMC_MESSAGE_*`, `SMC_RESP_*`, and `SMC_MSG_ARG_*` fields. These macros support host-driver communication with the SMU firmware through mailbox-style registers and indexed register access.

The reset, GPIO, RCU, and fuse blocks define fields for `SMC_SYSCON_*`, `GPIOPAD_*`, `RCU_UC_EVENTS`, `RCU_MISC_CTRL`, `CC_RCU_FUSES`, `CC_SMU_MISC_FUSES`, `CC_SCLK_VID_FUSES`, ID straps, and SMU firmware load/status registers. These describe boot sequencing, soft reset override, clock gating, GPIO interrupt setup/acknowledge, feature-disable fuses, silicon IDs, and firmware read/write state.

The largest section is the `DPM_TABLE_*` ABI starting at line 817. It maps a packed SMU dynamic power-management table into register-like 32-bit words. It covers graphics, memory, link, ACPI, UVD, VCE, ACP, and SAMU levels; voltage rails and SMIO tables; PLL/programming words; boot levels; polling intervals; thermal/voltage response timings; BAPM coefficients; TDP and FPS thresholds; DTE limits; boot voltages; and low-SCLK interrupt thresholds.

After the DPM table, the chunk defines firmware and runtime status fields: `FIRMWARE_FLAGS`, `TDC_STATUS`, current averages and VRM limits, and a broad `FEATURE_STATUS` bitmap for DPM/BAPM/LPMX/NBDPM/LHTC/VPC/voltage/TDC/GPU-CAC/AVS/SPMI enable and forced-state status.

The memory-controller tuning area defines a large `MCARB_DRAM_TIMING_TABLE_*` grid, then `MC_REGISTERS_TABLE_*` address/value arrays. These represent packed DRAM timing rows and memory-controller register programming tables consumed by SMU or powerplay code when changing memory clocks and related state.

The final visible families in this chunk cover fan and thermal behavior: `FAN_TABLE_*`, `SOFT_REGISTERS_TABLE_*`, `PM_FUSES_*`, `SMU_PM_STATUS_0` through `SMU_PM_STATUS_127`, `CG_THERMAL_*`, `CG_FDO_*`, `CG_TACH_*`, `CC_THM_STRAPS0`, and TMON read/debug data for `THM_TMON0_*` and `THM_TMON1_*`. The chunk then reaches `GENERAL_PWRMGT`, whose remaining fields continue after the assigned range.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, storage objects, or exported symbols in this chunk. The public interface is entirely preprocessor macros consumed by other AMDGPU driver code.

Important macro API conventions:

- `*_MASK` is the field mask already positioned in the 32-bit register word.
- `*__SHIFT` is the bit position used to right-shift extracted values or left-shift raw values before masking.
- Full-word fields use mask `0xffffffff` and shift `0x0`; these appear frequently for table entries, status data, message arguments, and raw data registers.
- Packed byte/halfword fields commonly use masks such as `0xff`, `0xff00`, `0xffff`, and `0xffff0000`, showing the expected serialized layout of SMU tables.

The macros are intended for use with existing AMDGPU helper idioms that read/write registers and update fields, such as code that performs `(value & FIELD_MASK) >> FIELD__SHIFT` or writes `(new_value << FIELD__SHIFT) & FIELD_MASK`. The header itself does not provide those helpers.

## Control Flow And State Behavior

This file has no runtime control flow. Its impact is compile-time name binding for hardware register operations elsewhere in the driver.

The state described by the macros is hardware and firmware state:

- Clock and PLL state lives in GPU registers and affects DCLK, VCLK, ECLK, ACLK, SCLK, DFS bypass paths, SPLL programming, spread spectrum, and clock-pin routing.
- SMC message and response state lives in SMU mailbox registers. Driver code writes message arguments and commands, then polls or reads response fields.
- Fuse and strap state is persistent silicon/board configuration exposed through read-only or special-purpose registers. These fields affect feature enablement, disabled blocks, revision IDs, voltage IDs, repair/test behavior, and boot restrictions.
- DPM, memory timing, fan, soft-register, and fuse tables are packed state shared with SMU firmware. Field order and bit positions are an ABI; wrong packing can change voltage/frequency, thermal, or memory-controller behavior.
- Status fields such as `FEATURE_STATUS`, `SMU_PM_STATUS_*`, `TDC_STATUS`, and thermal/TMON data are readback/telemetry state.

Because this is a header of constants, it persists only through source control and the compiled binary. It does not allocate memory, store data, or mutate state directly.

## Dependencies And Integration Points

This header belongs under `drivers/gpu/drm/amd/include/asic_reg/smu`, so its direct integration point is AMDGPU's ASIC-specific register programming code for SMU 7.1.0-era hardware. It is expected to be included alongside the corresponding offset header, commonly named with the same ASIC/register block and no `_sh_mask` suffix. The offset header supplies register addresses; this header supplies bit positions inside those registers.

Major downstream consumers are likely AMDGPU power-management and SMU support code that:

- Programs PLLs, dividers, bypasses, and spread spectrum for graphics, display/video, memory, and auxiliary clocks.
- Sends SMC messages through message/response/argument mailboxes and indirect SMC index/data windows.
- Reads fuses and straps to discover disabled IP, revision IDs, voltage limits, repair state, and security/test restrictions.
- Constructs or decodes SMU DPM tables for voltage/frequency levels across graphics, memory, PCIe link, UVD, VCE, ACP, and SAMU domains.
- Applies memory-controller timing/register tables during memory DPM transitions.
- Reads telemetry/status and configures thermal interrupts, fan PWM/tach behavior, and global power-management bits.

The file depends only on the C preprocessor. Its real dependency is on exact agreement with the ASIC register specification and SMU firmware table layout.

## Risks And Edge Cases

The main risk is ABI drift. `DPM_TABLE_*`, `MCARB_DRAM_TIMING_TABLE_*`, `MC_REGISTERS_TABLE_*`, `SOFT_REGISTERS_TABLE_*`, and `PM_FUSES_*` fields encode packed firmware table layouts. Changing a mask, shift, table index, or field name without a matching firmware/register-spec update can silently corrupt power, voltage, memory timing, or thermal policy.

The assigned range ends mid-register at `GENERAL_PWRMGT__GPU_COUNTER_ACPI_MASK`. Research or automated merge tooling must reconcile this chunk with the following chunk so the final per-file document does not imply `GENERAL_PWRMGT` is complete here.

Macro names are mechanically generated and easy to misuse because many fields are repeated by level or table index. Examples include graphics levels 0-7, memory levels 0-5, link levels 0-7, UVD/VCE/ACP/SAMU levels 0-7, 128 `SMU_PM_STATUS_*` data words, and repeated TMON `RDIL`/`RDIR` sensor fields. Copy/paste mistakes can compile cleanly while targeting the wrong table slot.

Several fields control hazardous hardware behavior: reset overrides, clock/PLL reset and bypass, voltage control, thermal protection disable/type, fan PWM manual mode, fuse disable bits, and memory-controller timing tables. Incorrect writes can cause hangs, overheating, display/video instability, memory errors, or loss of SMU communication.

Reserved and spare masks are exposed throughout the header. Driver code should avoid setting reserved bits unless the hardware specification explicitly requires a value; read-modify-write paths must preserve unrelated bits.

## Test Signals

Useful static checks:

- Build AMDGPU code paths that include this header and verify all generated macro names used by source files still resolve.
- Compare this header against the matching SMU 7.1.0 register database or offset header to detect missing, renamed, duplicated, or shifted fields.
- Validate that every field has both `*_MASK` and `*__SHIFT` definitions, and that each mask aligns with its shift.
- Check repeated table families for monotonic index continuity, especially `DPM_TABLE_*`, `MCARB_DRAM_TIMING_TABLE_*`, `MC_REGISTERS_TABLE_*`, and `SMU_PM_STATUS_*`.

Useful runtime/hardware signals:

- SMU firmware loads and reports expected `SMU_STATUS`, `SMU_FIRMWARE`, and mailbox responses.
- DPM enables/forces in `FEATURE_STATUS` reflect requested graphics, memory, PCIe, UVD, VCE, ACP, SAMU, BAPM, voltage, and thermal features.
- Clock, voltage, and PCIe link transitions complete without hangs, bad telemetry, or display/video regressions.
- Fan PWM/tach values, thermal interrupt status, TMON temperature valid bits, and high/low thermal thresholds behave under thermal stress.
- Memory DPM transitions pass display stability, memory stress, and suspend/resume testing, because memory timing/register table packing is heavily represented in this chunk.

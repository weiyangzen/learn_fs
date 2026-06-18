# subset-b-003427 grouped research

This grouped report covers AMDGPU ASIC register metadata headers for SMUIO and THM blocks. Each section is source-tree aligned and wrapped for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_8_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_8_sh_mask.h

## Purpose
`smuio_15_0_8_sh_mask.h` is the SMUIO 15.0.8 bitfield contract. It defines C preprocessor `__SHIFT` and `_MASK` macros for SMUIO register fields across time-stamp counter, software timer, miscellaneous identification/scratch, I2C, ROM, GPIO, and SMIO address blocks. The file contains no executable code; its purpose is to let AMDGPU register-access helpers encode and decode 32-bit MMIO values without embedding numeric bit positions at call sites.

## Important APIs, Types, And Macros
The file exports macros only. There are no functions, structs, enums, or global objects.

Important macro groups include:

- TSC and power-good timing fields: `PWROK_REFCLK_GAP_CYCLES`, `GOLDEN_TSC_INCREMENT_UPPER/LOWER`, `GOLDEN_TSC_COUNT_UPPER/LOWER`, `SOC_GOLDEN_TSC_SHADOW_UPPER/LOWER`, and `SOC_GAP_PWROK`.
- Software timer and interrupt fields: `PWR_VIRT_RESET_REQ` exposes `VF_FLR` and `PF_FLR`; `PWR_DISP_TIMER_CONTROL`, `PWR_DISP_TIMER2_CONTROL`, and debug/global-control variants define timer counts, enable/disable bits, interrupt masking, ACK, type, mode, pulse width, and run/status fields; `PWR_IH_CONTROL` defines interrupt-handler credit and timer trigger masks.
- Miscellaneous device metadata and scratch fields: `SMUIO_MCM_CONFIG` carries die/package/socket/topology bits, `IP_DISCOVERY_VERSION` is full width, and `SCRATCH_REGISTER0` through `SCRATCH_REGISTER7` are full-width scratch pads.
- Two DesignWare-style I2C controller field sets: `CKSVII2C_*` and `CKSVII2C1_*` cover controller configuration, target/slave addresses, data command bits, SCL timing counters, interrupt status/masks, FIFO thresholds, enable/status, SDA timing, component parameters, version, and type. The second controller mirrors the first with `1`-suffixed field names.
- `SMUIO_PWRMGT` controls I2C and I2C1 clock-gate and reset bits.
- ROM fields: `ROM_CNTL`, `PAGE_MIRROR_CNTL`, `ROM_STATUS`, `CGTT_ROM_CLK_CTRL0`, `ROM_INDEX`, `ROM_DATA`, `ROM_START`, `ROM_SW_CNTL`, `ROM_SW_STATUS`, `ROM_SW_COMMAND`, and `ROM_SW_DATA_1` through `ROM_SW_DATA_64`.
- GPIO/SMIO fields: `SMU_GPIOPAD_*`, `DFT_PINSTRAPS`, GPIO interrupt status/ACK/enable/type/polarity/select registers, MP interrupt status registers, `SMIO_INDEX`, `S0_VID_SMIO_CNTL`, `S1_VID_SMIO_CNTL`, `OPEN_DRAIN_SELECT`, and `SMIO_ENABLE`.

## Control Flow
There is no local control flow. The macros participate in control flow only when included by C files that call AMDGPU bitfield helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, or direct mask tests. Typical consumer flow is: read a register at an offset from the companion SMUIO offset header, isolate a field with the mask and shift defined here, branch on the decoded value, and optionally write back a modified register value.

Hardware flows represented by the fields include enabling or acknowledging display timers, polling ROM busy/done status, pushing ROM software commands and data words, programming I2C transfers, acknowledging GPIO interrupts through per-bit ACK fields, and selecting SMIO/GPIO routing. This header does not impose ordering; callers must follow hardware programming sequences from the SMU/SMUIO block specifications.

## State And Persistence Behavior
The header is compile-time metadata and stores no state. The state it describes is hardware state in SMUIO registers:

- Timer count, enable, status, ACK, and mask fields affect live interrupt delivery and persist until changed by software, hardware, or reset.
- Scratch registers and ROM software data registers are full-width payload/state registers shared with firmware or boot ROM flows.
- I2C interrupt, FIFO, enable, abort, status, and timing fields reflect or modify the state of on-chip I2C controllers.
- GPIO pad masks, output values, input status, pull-up/down, receiver selection, interrupt controls, pin straps, and SMIO settings represent externally visible pins and interrupt routing.
- TSC and power-good timing fields describe counters or gap settings that can affect timekeeping and power sequencing behavior.

## Dependencies
Consumers depend on this header matching the SMUIO 15.0.8 register offsets and silicon layout. It is normally used with the companion generated offset/default headers and AMDGPU/SOC15 register-access macros. The naming convention is significant: `REG_SET_FIELD(value, REGISTER, FIELD, new_value)` depends on the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` spelling exported here.

The include guard is `_smuio_15_0_8_SH_MASK_HEADER`. The file also depends on C preprocessor integer constants being wide enough for 32-bit masks; masks are written with an `L` suffix.

## Integration Points
This header integrates with the AMDGPU kernel driver register layer under `drivers/gpu/drm/amd`. It is generated-style ASIC metadata consumed by SMU, PSP, power-management, GPIO/I2C, ROM access, and platform discovery code paths for devices whose IP discovery tables identify SMUIO 15.0.8. It pairs with offset definitions for the same IP version; mixing this mask file with another generation's offsets can silently program the wrong bits.

## Risks
- Bitfield drift is high impact: a wrong mask or shift compiles cleanly but causes incorrect MMIO writes.
- Several registers use full-width masks, which do not validate firmware protocol payloads or restrict reserved values.
- The two I2C controllers are nearly mirrored but have different field names; copy/paste mistakes can select the wrong controller.
- GPIO and SMIO fields touch external pin behavior and interrupt routing. Incorrect programming can break board straps, GPIO interrupts, or open-drain behavior.
- ROM control fields include mode, timing, fast-mode, page-mirror, and auto-increment controls; wrong writes can break VBIOS/firmware ROM reads.
- `RESERVED` and undocumented high bits should not be treated as writable feature fields even when masks expose them.

## Test Signals
- Compile coverage of all consumers catches missing macro names but not wrong values.
- Hardware register trace tests should confirm timer, I2C, ROM, and GPIO writes hit the intended bit positions.
- ROM read tests should validate index/data access, software command completion, and busy polling.
- I2C tests should cover normal transfers, FIFO threshold interrupts, abort paths, SCL/SDA stuck recovery, and both controller instances.
- GPIO tests should cover pad direction, interrupt status/ACK, polarity/type programming, and SMIO selection.
- Cross-generation review should compare SMUIO 15.0.8 against earlier SMUIO headers before reusing code assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_15_0_8_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_offset.h

## Purpose
`smuio_9_0_offset.h` defines SMUIO 9.0 register offsets for the `smuio_smuio_SmuSmuioDec` address block whose documented base address is `0x5a000`. It maps symbolic `mm...` register names to register indices and supplies a matching `..._BASE_IDX` macro for each exported register.

## Important APIs, Types, And Macros
The header exports constants only. There are no functions, structs, enums, or runtime data.

The main register set covers ROM access and ROM software-command staging:

- ROM control/status/index/data/start registers: `mmROM_CNTL`, `mmROM_STATUS`, `mmCGTT_ROM_CLK_CTRL0`, `mmROM_INDEX`, `mmROM_DATA`, and `mmROM_START`.
- ROM software-command registers: `mmROM_SW_CNTL`, `mmROM_SW_STATUS`, `mmROM_SW_COMMAND`, and `mmROM_SW_DATA_1` through `mmROM_SW_DATA_64`, arranged contiguously from offsets `0x002e` through `0x006d`.
- SVI telemetry/current-voltage registers: `mmSMUSVI0_PLANE0_CURRENTVID` at offset `0x0013` and `mmSMUSVI0_TEL_PLANE0` at offset `0x0004`.

Every register is paired with `_BASE_IDX 0`, indicating that consumers should use register base index `0` with the AMDGPU register-access macros for this block.

## Control Flow
There is no local control flow. Consumer flow is data driven: include this offset header, include the matching `smuio_9_0_sh_mask.h`, then use SOC15/MMIO helpers to read or write registers by symbolic name. ROM-read code typically programs `ROM_INDEX` or `ROM_SW_COMMAND`, reads or writes `ROM_DATA`/`ROM_SW_DATA_n`, and polls status fields defined in the shift/mask header.

## State And Persistence Behavior
The header is stateless. It names MMIO locations whose values persist in hardware until changed by firmware, software, or device reset:

- ROM index/data/control state affects firmware or VBIOS ROM access.
- `ROM_SW_DATA_1` through `ROM_SW_DATA_64` provide command payload or return-data staging for software ROM commands.
- SVI registers expose voltage/telemetry information from the SMU/SVI interface.

## Dependencies
This header depends on consumers using the same SMUIO 9.0 address-map generation as the matching shift/mask header. It is normally consumed through AMDGPU register helpers that combine the `mm...` offset with `..._BASE_IDX`. The exact macro spelling is part of the generated AMD register ABI.

## Integration Points
The file integrates with AMDGPU ASIC support for SMUIO 9.0 devices. It is paired with `smuio_9_0_sh_mask.h`, which defines the fields inside the offsets named here. ROM, VBIOS, SMU telemetry, and power-management paths are likely consumers because those paths need ROM data, ROM command status, and SVI voltage fields.

## Risks
- Offset mismatch can cause reads and writes to target the wrong SMUIO register while still compiling.
- The long contiguous `ROM_SW_DATA_n` range is easy to index incorrectly in hand-written loops; consumers must preserve the one-based naming and actual offsets.
- Mixing this 9.0 offset header with a newer mask header is unsafe because newer generations add fields and may alter bit layout.
- Base index is uniformly `0`; any code assuming a nonzero instance or broadcast base would misaddress this block.

## Test Signals
- Build coverage verifies that symbolic offsets exist.
- ROM access tests should confirm `ROM_INDEX`, `ROM_DATA`, `ROM_SW_COMMAND`, and all expected payload registers address the correct hardware locations.
- SVI telemetry tests should compare decoded `CURRENTVID` and `TEL_PLANE0` values against expected SMU telemetry.
- Register dumps from known SMUIO 9.0 hardware should match the base `0x5a000` block layout and listed offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_sh_mask.h

## Purpose
`smuio_9_0_sh_mask.h` is the SMUIO 9.0 companion bitfield header for `smuio_9_0_offset.h`. It defines `__SHIFT` and `_MASK` macros for ROM control/status, ROM software-command registers, ROM payload registers, and two SVI telemetry fields.

## Important APIs, Types, And Macros
The file exports macros only. It defines no functions, types, or storage.

Important fields include:

- `ROM_CNTL__CLOCK_GATING_EN` for ROM clock gating.
- `ROM_STATUS__ROM_BUSY` for ROM busy polling.
- `CGTT_ROM_CLK_CTRL0` fields for clock-gating timing: `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_OVERRIDE1`, and `SOFT_OVERRIDE0`.
- `ROM_INDEX`, `ROM_DATA`, and `ROM_START` full-address/data fields. Index and start are masked to 24 bits in this generation.
- `ROM_SW_CNTL` fields for software command data size, command size, and return-data enable.
- `ROM_SW_STATUS__ROM_SW_DONE` for command-completion polling.
- `ROM_SW_COMMAND` fields for an 8-bit instruction and upper address bits.
- `ROM_SW_DATA_1` through `ROM_SW_DATA_64` full-width payload fields.
- `SMUSVI0_PLANE0_CURRENTVID__CURRENT_SVI0_PLANE0_VID` at bits `31:24`.
- `SMUSVI0_TEL_PLANE0__SVI0_PLANE0_VDDCOR` at bits `24:16` via mask `0x01FF0000L`.

## Control Flow
There is no executable control flow. Consumers use the macros to implement ROM and telemetry control sequences. A ROM software-command path would set data and command size in `ROM_SW_CNTL`, place an instruction/address in `ROM_SW_COMMAND`, fill or read `ROM_SW_DATA_n`, and poll `ROM_SW_STATUS.ROM_SW_DONE`. A simple indexed ROM read path would program `ROM_INDEX` or `ROM_START`, read `ROM_DATA`, and poll `ROM_STATUS.ROM_BUSY` as needed.

## State And Persistence Behavior
The header itself is stateless. It describes live hardware register fields:

- Clock-gating fields affect ROM block power/clock behavior until changed.
- ROM busy/done bits are hardware status indicators.
- ROM command, address, and data fields are transient payload staging state for firmware/ROM operations.
- SVI fields expose current voltage ID and telemetry data from the SVI plane.

## Dependencies
The macros depend on the offsets from `smuio_9_0_offset.h` and the AMDGPU bitfield-helper naming convention. Any consumer using `REG_GET_FIELD` or `REG_SET_FIELD` requires both `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` to be present and correct.

## Integration Points
This header integrates with AMDGPU support for SMUIO 9.0 ASICs, especially ROM/VBIOS access, SMU firmware loading or command paths, and power telemetry paths that read SVI voltage information. It is part of the generated AMD ASIC register include tree under `include/asic_reg`.

## Risks
- Incorrect `ROM_SW_CNTL` field widths would corrupt software-command packet framing.
- Incorrect `ROM_SW_STATUS` or `ROM_STATUS` masks can create premature completion, stuck polling, or timeout behavior.
- Full-width `ROM_SW_DATA_n` masks do not protect against protocol-level invalid payloads.
- The SVI fields are narrow high-bit slices; using the raw register without mask/shift would report incorrect voltage values.
- SMUIO 9.0 ROM field widths differ from newer SMUIO generations, so cross-generation assumptions are risky.

## Test Signals
- Compile checks catch missing macro names.
- Hardware ROM tests should validate busy/done polling and data returned from indexed and software-command reads.
- Firmware-loading or VBIOS-read smoke tests exercise the ROM command/data fields indirectly.
- Power telemetry tests should confirm decoded SVI current VID and VDDCOR values against SMU-reported values.
- Register-generation validation should compare masks against the official SMUIO 9.0 address map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_default.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_default.h

## Purpose
`thm_10_0_default.h` defines reset/default values for THM 10.0 registers in the `thm_thm_SmuThmDec` address block. It is generated-style metadata used by AMDGPU code and register tooling to understand expected power-on values for thermal, temperature-monitor, SBI/SBRMI, SMBus, and remote-monitor registers.

## Important APIs, Types, And Macros
The header exports `mm..._DEFAULT` constants only. There are no functions, structs, enums, or stateful objects.

Important default groups include:

- Thermal controller and interrupt defaults: `mmTHM_TCON_CUR_TMP_DEFAULT`, `mmTHM_TCON_HTC_DEFAULT`, `mmTHM_TCON_THERM_TRIP_DEFAULT`, `mmTHM_CTF_DELAY_DEFAULT`, `mmTHM_GPIO_PROCHOT_CTRL_DEFAULT`, `mmTHM_THERMAL_INT_ENA_DEFAULT`, `mmTHM_THERMAL_INT_CTRL_DEFAULT`, and `mmTHM_THERMAL_INT_STATUS_DEFAULT`.
- Temperature monitor data defaults: `mmTHM_TMON0_RDIL0_DATA_DEFAULT` through `RDIL15`, `mmTHM_TMON0_RDIR0_DATA_DEFAULT` through `RDIR15`, `mmTHM_TMON0_INT_DATA_DEFAULT`, `mmTHM_TMON0_CTRL_DEFAULT`, `mmTHM_TMON0_CTRL2_DEFAULT`, and `mmTHM_TMON0_DEBUG_DEFAULT`.
- Temperature and clock-gating/thermal-range defaults: `mmTHM_DIE1_TEMP_DEFAULT`, `mmTHM_DIE2_TEMP_DEFAULT`, `mmTHM_DIE3_TEMP_DEFAULT`, `mmTHM_SW_TEMP_DEFAULT`, `mmCG_MULT_THERMAL_CTRL_DEFAULT`, `mmCG_MULT_THERMAL_STATUS_DEFAULT`, and `mmCG_THERMAL_RANGE_DEFAULT`.
- TMON configuration/calibration defaults: `mmTHM_TMON_CONFIG_DEFAULT`, `mmTHM_TMON_CONFIG2_DEFAULT`, `mmTHM_TMON0_COEFF_DEFAULT`, and local threshold/control registers `mmTHM_TCON_LOCAL0_DEFAULT` through `LOCAL13`.
- Power-management, SBI, SBTSI, SBRMI, and SMBus defaults: `mmTHM_PWRMGT_DEFAULT`, `mmSMUSBI_*_DEFAULT`, `mmSBTSI_REMOTE_TEMP_DEFAULT`, `mmSBRMI_*_DEFAULT`, `mmSMBUS_*_DEFAULT`, `mmSMUSBI_SMBUS_DEFAULT`, and `mmSMUSBI_ALERT_DEFAULT`.
- Remote TMON range defaults for `TMON0` through `TMON3`, each with start and end registers defaulting to zero.

## Control Flow
There is no executable control flow. Consumers use these constants for register reset verification, golden-setting comparison, diagnostics, or generated initialization metadata. Runtime thermal-control code would use the companion offset and shift/mask headers for actual register access; this header only provides expected default values.

## State And Persistence Behavior
The header is stateless. The values describe hardware state after reset or default initialization. Many defaults are zero, but several registers have meaningful nonzero defaults, including thermal trip/control, PROCHOT GPIO control, thermal interrupt control, TMON control/config/coefficient values, `CG_MULT_THERMAL_CTRL`, `THM_PWRMGT`, SBI timing/control, SMBus control/timing/UDID fields, and SBRMI core-enable count. These defaults may be overwritten by firmware, BIOS, SMU, or driver initialization after reset.

## Dependencies
This file depends on the THM 10.0 address map and pairs with `thm_10_0_offset.h` and shift/mask definitions for the same generation. Consumers must not treat defaults as writable masks; they are complete reset-value constants.

## Integration Points
The header integrates with AMDGPU thermal-management support, SMU diagnostics, register dump tooling, and any golden-register validation paths that compare live THM registers against expected reset values. It is especially relevant to thermal interrupt setup, PROCHOT handling, SMBus/SBI sideband communication, and SBRMI remote-management state.

## Risks
- Treating defaults as mandatory runtime values can overwrite firmware-calibrated thermal settings.
- Nonzero defaults encode important board/IP assumptions, such as SMBus timing and TMON coefficients; accidental edits can invalidate diagnostics.
- Reset defaults may not match post-BIOS or post-SMU state, so tests must distinguish reset validation from runtime policy validation.
- SMBus and SBRMI defaults affect sideband-management expectations; mismatches can be misdiagnosed as communication failures.

## Test Signals
- Register-dump comparison after cold reset should match documented defaults before firmware or driver policy changes.
- Thermal bring-up tests should verify that nonzero defaults such as `THM_TCON_HTC`, `THM_THERMAL_INT_CTRL`, `THM_TMON_CONFIG`, and `THM_TMON0_COEFF` are sane for the ASIC.
- SMBus/SBI/SBRMI tests should validate timing and control defaults before active transactions.
- Runtime tests should verify that driver initialization may intentionally diverge from these defaults without being reported as an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_default.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_offset.h

## Purpose
`thm_10_0_offset.h` defines THM 10.0 MMIO register offsets for the `thm_thm_SmuThmDec` address block whose documented base address is `0x59800`. It maps thermal, TMON, SBI, SBRMI, SMBus, and remote temperature-monitor registers to symbolic `mm...` offsets and supplies a matching `..._BASE_IDX` macro for each register.

## Important APIs, Types, And Macros
The header exports constants only. There are no functions, structs, enums, or runtime objects.

Important register groups include:

- Thermal controller and interrupt registers from offsets `0x0000` through `0x000c`, including current temperature, HTC, thermal trip, CTF delay, GPIO PROCHOT control, thermal interrupt enable/control/status.
- TMON0 local data and control registers from `0x000d` through `0x0030`, including `RDIL0..15`, `RDIR0..15`, interrupt data, control, control2, and debug.
- Die/software temperature and thermal configuration registers at `0x0055` through `0x005e`, including `DIE1_TEMP`, `DIE2_TEMP`, `DIE3_TEMP`, `SW_TEMP`, `CG_MULT_THERMAL_CTRL/STATUS`, `CG_THERMAL_RANGE`, `THM_TMON_CONFIG`, `THM_TMON_CONFIG2`, and `THM_TMON0_COEFF`.
- Local thermal controller registers `THM_TCON_LOCAL0` through `LOCAL13` at `0x006e` through `0x007b`, plus `THM_PWRMGT` at `0x007d`.
- SBI/SBTSI/SBRMI registers from `0x0080` through `0x0098`, covering SBI address/data/control/timing, remote temperature, SBRMI command/write/read data, core-enable status, APIC status, and MCE status.
- SMBus and alert registers from `0x0099` through `0x00a7`, including control, block read/write command control, timing control, trigger, UDID, SMUSBI SMBus, and alert.
- Remote TMON window ranges: `THM_TMON0_REMOTE_START/END` through `THM_TMON3_REMOTE_START/END`, spanning `0x0100` through `0x01ff` by range endpoints.

All listed registers use `_BASE_IDX 0`.

## Control Flow
There is no local control flow. Consumer code uses these offsets with THM mask/default headers and AMDGPU MMIO helpers to read temperatures, configure interrupts, handle PROCHOT/thermal trips, program temperature monitor windows, and communicate over SBI/SBRMI/SMBus sideband interfaces.

## State And Persistence Behavior
The header is stateless, but the named registers hold thermal-management state:

- Temperature and status registers reflect live sensor, interrupt, and thermal-trip state.
- Control registers configure thermal thresholds, PROCHOT GPIO behavior, TMON behavior, power management, and interrupt routing.
- SBI, SBRMI, and SMBus registers hold sideband command/data/timing state.
- Remote TMON start/end ranges define monitored remote regions until reprogrammed.

Values persist in hardware until reset or rewritten by BIOS, firmware, SMU, or driver code.

## Dependencies
This header depends on the THM 10.0 register map and should be used with `thm_10_0_default.h` and the matching THM shift/mask header for field-level access. The `mm...` and `_BASE_IDX` macro names must match the AMDGPU register-access conventions.

## Integration Points
The offsets integrate with AMDGPU thermal and power-management code, SMU/PM firmware interactions, register dump tools, and sideband-management paths. They provide the address layer for temperature readings, thermal interrupt programming, SMBus/SBI/SBRMI transactions, and TMON remote monitoring on THM 10.0 ASICs.

## Risks
- Offset errors in thermal-control registers can break over-temperature protection or PROCHOT behavior.
- Misaddressed SMBus/SBI/SBRMI registers can corrupt sideband transactions and make platform-management failures hard to diagnose.
- Remote TMON ranges are represented by start/end offsets rather than every element in the range; code iterating those windows must derive intermediate addresses correctly.
- The base index is uniformly `0`; consumers must not assume multiple THM instances without checking the IP discovery data.
- Combining this offset header with another generation's shift/mask/default header can silently decode or program wrong fields.

## Test Signals
- Thermal sensor tests should read current, die, and software temperature registers and compare them with SMU-reported temperatures.
- Thermal interrupt tests should exercise enable/control/status paths and verify ACK/clear behavior through the companion mask header.
- PROCHOT and thermal-trip validation should confirm the expected registers at the documented offsets are affected.
- SMBus/SBI/SBRMI transaction tests should verify command/data/timing offsets against hardware traces.
- Register dump validation should confirm the THM 10.0 block starts at base `0x59800` and all offsets land on expected registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_offset.h -->

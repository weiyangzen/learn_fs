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

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_2_sh_mask.h

## Purpose

`smuio_13_0_2_sh_mask.h` is a generated AMDGPU SMUIO 13.0.2 register-field header. It does not implement executable logic; it exports C preprocessor constants that define bit shifts and already-positioned masks for fields inside SMUIO registers. The companion offset header supplies register addresses, while this file supplies the field layout for those addresses.

The file is broader than a simple MCM-identification mask set. It covers SMU voltage/I2C telemetry registers, MCM/package topology fields, two CKSVII2C controller instances, reset and power-management fields, ROM and ROM software-command registers, GPIO pad and pinstrap registers, PCC/SMIO controls, IP discovery, golden TSC/power-good timing, scratch registers, and display power timer interrupt controls.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, global variables, or inline helpers. The public API is the macro namespace:

- `REGISTER__FIELD__SHIFT` gives the right-shift amount for a field.
- `REGISTER__FIELD_MASK` gives the field mask in its final register position.

Important macro groups include:

- `SMUSVI0_TEL_PLANE0` and `SMUSVI0_PLANE0_CURRENTVID`: SVI voltage/current telemetry fields for plane 0.
- `SMUIO_MCM_CONFIG`: die, package type, socket, package subtype, and topology fields. These are consumed by SMUIO code through `REG_GET_FIELD()` to identify die/socket/package/topology properties.
- `CKSVII2C_*` and `CKSVII2C1_*`: two DesignWare-style I2C register layouts covering master/slave mode, target/slave addressing, data commands, SCL timing, interrupt status/mask, FIFO thresholds and levels, enable/status, SDA hold/setup, spike length, component parameters, version, and type.
- `SMUIO_MP_RESET_INTR`, `SMUIO_SOC_HALT`, `SMUIO_PWRMGT`, and `SMUIO_GFX_MISC_CNTL`: reset, halt/watchdog, I2C clock gating, and graphics miscellaneous control fields.
- `ROM_CNTL`, `PAGE_MIRROR_CNTL`, `ROM_STATUS`, `CGTT_ROM_CLK_CTRL0`, `ROM_INDEX`, `ROM_DATA`, `ROM_START`, `ROM_SW_CNTL`, `ROM_SW_STATUS`, `ROM_SW_COMMAND`, and `ROM_SW_DATA_1` through `ROM_SW_DATA_64`: BIOS ROM access, clock gating, page mirror, SPI command, index/data, and software-command payload fields.
- `SMU_GPIOPAD_*`, `DFT_PINSTRAPS`, `ROM_CC_BIF_PINSTRAP`, `IO_SMUIO_PINSTRAP`, `SMUIO_PCC_CONTROL`, `SMUIO_PCC_GPIO_SELECT`, `SMUIO_GPIO_INT*_SELECT`, `SMIO_INDEX`, `S0_VID_SMIO_CNTL`, `S1_VID_SMIO_CNTL`, `OPEN_DRAIN_SELECT`, and `SMIO_ENABLE`: GPIO, pinstrap, board configuration, interrupt select/status/ack, open-drain, and SMIO state fields.
- Power/TSC groups such as `IP_DISCOVERY_VERSION`, `SOC_GAP_PWROK`, `GFX_GAP_PWROK`, `PWROK_REFCLK_GAP_CYCLES`, `GOLDEN_TSC_*`, `SOC_GOLDEN_TSC_SHADOW_*`, `GFX_GOLDEN_TSC_SHADOW_*`, scratch registers, and `PWR_DISP_TIMER*` interrupt control/debug fields.

## Control Flow And Data Flow

The header has no runtime control flow. Driver data flow is:

1. Include this field header together with `smuio_13_0_2_offset.h`.
2. Select a register offset such as `regSMUIO_MCM_CONFIG`, `regCGTT_ROM_CLK_CTRL0`, `regROM_INDEX`, or an I2C/GPIO/PWR register from the companion offset header.
3. Read or write the register via AMDGPU SOC15 MMIO helpers such as `RREG32_SOC15()`, `WREG32_SOC15()`, or `SOC15_REG_OFFSET()`.
4. Decode or compose fields using `REG_GET_FIELD()` or explicit mask/shift operations.

Observed consumers include `amdgpu/smuio_v13_0.c`, which uses `SMUIO_MCM_CONFIG` fields for die/socket/topology/package detection and uses `CGTT_ROM_CLK_CTRL0` soft-override masks for ROM memory clock gating. It also exposes `regROM_INDEX` and `regROM_DATA` offsets through `amdgpu_smuio_funcs`. `pm/swsmu/smu13/smu_v13_0.c` also includes the 13.0.2 SMUIO offset and mask headers, so this macro set is part of the SMU firmware-management register surface.

## State And Persistence Behavior

This header stores no software state. Its constants describe hardware state that persists in SMUIO registers until changed by the driver, firmware, reset, strap sampling, or power-management transitions. Representative state includes:

- Package identity and topology in `SMUIO_MCM_CONFIG`.
- ROM access state, SPI timing mode, software-command payload words, ROM busy/done status, and ROM clock-gating overrides.
- I2C controller configuration, FIFO status, interrupt state, abort/enable state, and timing parameters for two controller instances.
- GPIO pad direction, output, receiver, pull-up/down, pinstrap, interrupt, open-drain, SMIO, and PCC selection state.
- Power-good gap state, golden TSC increments/counts/shadows, scratch registers, and display timer interrupt status/control.

Because these masks are a hardware ABI description, a wrong shift or mask can make persistent device state incorrect until reset or later corrective programming.

## Dependencies And Integration Points

The only direct dependency is the C preprocessor. In practice the file is paired with matching SMUIO 13.0.2 register offsets and AMDGPU bitfield/MMIO helpers:

- `smuio_13_0_2_offset.h` for `reg*` addresses and base-index values.
- `amdgpu/smuio_v13_0.c` for MCM identity queries, host-GPU XGMI topology detection, package type inference, ROM index/data offset lookup, and ROM clock-gating control.
- `pm/swsmu/smu13/smu_v13_0.c` for SMU 13.0 register access.
- AMDGPU SOC15 macros such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `REG_GET_FIELD`.

The header is also indirectly tied to device-family selection: consumers must use the matching SMUIO version for the ASIC they are programming.

## Risks And Edge Cases

- Generated register data is easy to break with manual edits. Compile-time coverage catches missing names, but rarely proves masks are semantically correct.
- The same macro names, especially `SMUIO_MCM_CONFIG`, exist across many SMUIO generations with different bit positions. Including or pairing the wrong generation can silently decode package, die, socket, or topology fields incorrectly.
- ROM and page-mirror fields affect firmware/BIOS ROM access. Bad writes can hang ROM transactions, return corrupt data, or defeat expected clock-gating behavior.
- I2C fields include abort, enable, FIFO, interrupt, timing, and DMA-related fields. Incorrect values can wedge an I2C controller or lose interrupt/error events.
- GPIO and pinstrap fields represent board- and strap-sensitive state. Consumers should preserve reserved bits and avoid writing strap/status registers as if they were ordinary RAM.
- Some status/acknowledge fields are conventionally write-one-to-clear or read-clear in hardware blocks. The mask header does not encode access semantics, so code must rely on the hardware programming guide or existing driver patterns.

## Test Signals

Useful validation signals are hardware-oriented:

- Build AMDGPU configurations that include SMUIO 13.0.2 headers and consumers.
- Probe matching ASICs and verify `smuio_v13_0_funcs` reports stable die ID, socket ID, package type, and host-GPU XGMI support.
- Exercise VBIOS/ROM reads through `regROM_INDEX` and `regROM_DATA`, including suspend/resume and reset paths.
- Verify ROM clock-gating state transitions on supported discrete GPUs and confirm APUs skip unsupported ROM CG access.
- Run SMU 13.0 power-management tests that touch SMUIO telemetry, scratch, timing, or interrupt registers.
- Compare regenerated masks against AMD's canonical register database to catch field drift.

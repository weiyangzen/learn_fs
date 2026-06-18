# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_0_sh_mask.h

## Purpose

`smuio_11_0_0_sh_mask.h` is a generated AMDGPU SMUIO 11.0.0 bitfield header. It does not implement executable logic; it publishes `*_SHIFT` and `*_MASK` macros for registers in the `smuio_smuio_SmuSmuioDec` and `smuio_smuio_pwr_SmuSmuioDec` address blocks. The companion offset header supplies register addresses, while this file supplies the bit extraction and update constants used by `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, and manual mask/shift operations.

## Important APIs, Types, and Macros

The header exports C preprocessor macros only. There are no functions, structs, enums, or storage definitions.

Key macro groups:

- `SMUSVI0_TEL_PLANE0__SVI0_PLANE0_IDDCOR_*` and `SMUSVI0_TEL_PLANE0__SVI0_PLANE0_VDDCOR_*` expose voltage/current telemetry fields. `pm/swsmu/smu11/smu_v11_0.c` and older PowerPlay code use the VDDCOR field to compute current voltage.
- `SMUIO_MCM_CONFIG__DIE_ID_*`, `PKG_TYPE`, `SOCKET_ID`, and `PKG_SUBTYPE` describe package topology fields. Similar names are consumed through `REG_GET_FIELD` in newer SMUIO versions.
- `CKSVII2C_*` and `CKSVII2C1_*` cover two DesignWare-style I2C controllers: control, target/source address, data command, SCL timing, interrupt status/mask/raw status, FIFO levels, clear-on-read interrupt registers, enable/status, abort source, DMA thresholds, SDA hold/setup, spike length, and component ID/version/type registers.
- `SMUIO_MP_RESET_INTR`, `SMUIO_SOC_HALT`, and `SMUIO_PWRMGT` expose reset, watchdog force, and I2C clock-gating control bits.
- `ROM_CNTL`, `PAGE_MIRROR_CNTL`, `ROM_STATUS`, `CGTT_ROM_CLK_CTRL0`, `ROM_INDEX`, `ROM_DATA`, `ROM_START`, `ROM_SW_CNTL`, `ROM_SW_STATUS`, `ROM_SW_COMMAND`, and `ROM_SW_DATA_1` through `ROM_SW_DATA_64` describe VBIOS ROM access, ROM clock gating, software-command transfer sizing, and a 64-register data window.
- `SMU_GPIOPAD_*`, `DFT_PINSTRAPS`, `ROM_CC_BIF_PINSTRAP`, and `IO_SMUIO_PINSTRAP` define GPIO pad controls, pinstrap latches, GPIO interrupt status/enable/type/polarity/ack fields, BIF/ROM strap fields, and board/audio/SMBus strap fields.
- `SMUIO_PCC_*`, `SMUIO_GPIO_INT*_SELECT`, `SMU_GPIOPAD_MP_INT*_STAT`, `SMIO_INDEX`, `S0_VID_SMIO_CNTL`, `S1_VID_SMIO_CNTL`, `OPEN_DRAIN_SELECT`, `SMIO_ENABLE`, `SMU_GPIOPAD_S0`, `SMU_GPIOPAD_S1`, `SMU_GPIOPAD_SCL_EN`, `SMU_GPIOPAD_SDA_EN`, and `SMU_GPIOPAD_SCHMEN` define SMIO/GPIO routing and electrical configuration fields.
- Power-block macros include `IP_DISCOVERY_VERSION`, `SOC_GAP_PWROK`, `GFX_GAP_PWROK`, `PWROK_REFCLK_GAP_CYCLES`, golden TSC increment/count/shadow fields, `PWR_VIRT_RESET_REQ`, scratch registers, display timer controls, display timer global control, and `PWR_IH_CONTROL`.

## Control Flow

There is no internal control flow. All behavior comes from call sites that include this header:

- SMU11 power-management code reads `mmSMUSVI0_TEL_PLANE0`, masks with `SMUSVI0_TEL_PLANE0__SVI0_PLANE0_VDDCOR_MASK`, then shifts by `SMUSVI0_TEL_PLANE0__SVI0_PLANE0_VDDCOR__SHIFT`.
- `amdgpu/smuio_v11_0.c` reads `mmCGTT_ROM_CLK_CTRL0`, clears `CGTT_ROM_CLK_CTRL0__SOFT_OVERRIDE0_MASK` and `SOFT_OVERRIDE1_MASK` to enable ROM MGCG, or sets them to disable ROM clock gating. It returns early for APUs and checks `AMD_CG_SUPPORT_ROM_MGCG`.
- The same SMUIO implementation returns SOC15 offsets for `mmROM_INDEX` and `mmROM_DATA`, which are later used by AMDGPU ROM-reading paths.
- I2C users, when present, treat the `CKSVII2C*` macros as the canonical field map for programming controller enable, transfer, timing, interrupt, and abort/status registers.

## State and Persistence Behavior

The header itself has no runtime state and persists no data. Its macro values map to hardware register fields whose state is owned by the GPU/SMU hardware:

- ROM clock-gating bits in `CGTT_ROM_CLK_CTRL0` persist in the MMIO register until the driver or firmware changes them, and they are sampled for `AMD_CG_SUPPORT_ROM_MGCG` reporting.
- ROM index/data and software ROM data windows are transient hardware interfaces for reading firmware image data.
- GPIO, pinstrap, scratch, FLR, power-good, TSC, and display-timer registers represent hardware latch/configuration/state. Some fields are clear-on-read or ack-on-write style, as implied by `CLR_*` and `*_AK` names.

## Dependencies

This header depends only on the C preprocessor and include guard `_smuio_11_0_0_SH_MASK_HEADER`. It is meaningful only when paired with the correct 11.0.0 offset header and SOC15 register access helpers. Downstream code depends on AMDGPU infrastructure macros/functions such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and driver flags like `AMD_IS_APU` and `AMD_CG_SUPPORT_ROM_MGCG`.

## Integration Points

Direct includes found in this tree:

- `drivers/gpu/drm/amd/pm/swsmu/smu11/smu_v11_0.c`
- `drivers/gpu/drm/amd/amdgpu/smu_v11_0_i2c.c`
- `drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`
- `drivers/gpu/drm/amd/amdgpu/smuio_v11_0.c`

Representative integration:

- SMU11 voltage telemetry and PowerPlay telemetry use `SMUSVI0_TEL_PLANE0` masks.
- SMUIO 11 ROM helpers use `ROM_INDEX`, `ROM_DATA`, and `CGTT_ROM_CLK_CTRL0` fields.
- Graphics and I2C support code includes this mask map to avoid duplicate bit definitions.

## Risks and Edge Cases

- Generated field maps are hardware contracts; a wrong mask or shift silently corrupts MMIO operations. The risk is highest for write paths such as ROM clock-gating override, GPIO interrupt ack, reset, FLR, and power controls.
- Several registers are hardware status or clear/ack interfaces. Treating `CLR_*` or `*_AK` registers like ordinary read/write state can drop interrupts or acknowledge events unexpectedly.
- The file contains broad register coverage, but consumers may include only a small subset. Dead-looking macros should not be pruned without checking chipset-specific code paths.
- `CKSVII2C_IC_RAW_INTR_STAT__R_TX_EMPTY__SHIFT` appears with the misspelled macro prefix `CKSVII2C_IC__RAW_INTR_STAT__...`; consumers expecting the consistent `CKSVII2C_IC_RAW_INTR_STAT__R_TX_EMPTY__SHIFT` spelling would not find that specific shift macro.
- Bit widths differ across SMUIO versions, for example ROM index width is 24 bits here while 11.0.6 uses a 25-bit mask. Cross-version code must include the matching header for the selected IP.

## Test Signals

Useful validation signals are compile-time and hardware-integration oriented:

- Kernel build coverage for `smuio_v11_0.c`, `smu_v11_0_i2c.c`, `gfx_v10_0.c`, and SMU11 power-management files catches missing or renamed macros.
- Runtime ROM read tests exercise `ROM_INDEX`/`ROM_DATA` offsets and `CGTT_ROM_CLK_CTRL0` clock-gating behavior.
- Power-management telemetry tests can compare VDDCOR extraction against expected SMU sensor values.
- Suspend/resume and clock-gating tests should verify `AMD_CG_SUPPORT_ROM_MGCG` reporting and that APUs skip unavailable ROM clock-gating registers.
- GPIO/I2C tests should focus on interrupt clear/ack behavior, FIFO status, abort-source reporting, and controller enable/disable sequencing.

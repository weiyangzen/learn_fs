# Research: subset-b-003423

Grouped research for AMD SMUIO generated register headers. Each section preserves the exact source path in its title and is bounded for reconciliation into source-tree-aligned per-file outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_0_sh_mask.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_6_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_6_offset.h

## Purpose

`smuio_11_0_6_offset.h` is the SMUIO 11.0.6 generated register-offset header for the small ROM access subset used by AMDGPU. It maps symbolic `mm*` register names to offsets within the `smuio_smuio_SmuSmuioDec` address block, whose base address is documented as `0x5a000`.

## Important APIs, Types, and Macros

The header exports macro constants only:

- `mmCGTT_ROM_CLK_CTRL0` at offset `0x00e4`, base index `0`.
- `mmROM_INDEX` at offset `0x00e5`, base index `0`.
- `mmROM_DATA` at offset `0x00e6`, base index `0`.

There are no functions, types, or variables. These macros are passed to SOC15 helpers that combine IP block, instance, base index, and offset into an MMIO address.

## Control Flow

No control flow is implemented here. In `amdgpu/smuio_v11_0_6.c`, the macros drive this runtime sequence:

- `smuio_v11_0_6_get_rom_index_offset()` returns `SOC15_REG_OFFSET(SMUIO, 0, mmROM_INDEX)`.
- `smuio_v11_0_6_get_rom_data_offset()` returns `SOC15_REG_OFFSET(SMUIO, 0, mmROM_DATA)`.
- `smuio_v11_0_6_update_rom_clock_gating()` reads `mmCGTT_ROM_CLK_CTRL0`, updates the soft override bits supplied by the matching mask header, and writes the register only if the value changes.
- `smuio_v11_0_6_get_clock_gating_state()` reads `mmCGTT_ROM_CLK_CTRL0` and reports ROM MGCG support when override bit 0 is not set.

## State and Persistence Behavior

The header has no state. It names hardware registers whose state is persistent only in the device:

- `mmCGTT_ROM_CLK_CTRL0` controls/reflects ROM clock-gating timing and soft override state.
- `mmROM_INDEX` and `mmROM_DATA` form a hardware register pair for indexed ROM access.

Driver writes to `mmCGTT_ROM_CLK_CTRL0` survive until device reset, firmware action, or another driver path changes the register. ROM index/data usage is transient during VBIOS or ROM reads.

## Dependencies

The file depends on include guard `_smuio_11_0_6_OFFSET_HEADER` and the generated naming convention expected by AMDGPU SOC15 access macros. It must be paired with `smuio_11_0_6_sh_mask.h` for field-level operations. The runtime consumer depends on `amdgpu_device`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `AMD_IS_APU`, and `AMD_CG_SUPPORT_ROM_MGCG`.

## Integration Points

Direct include:

- `drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.c`

Functional integration:

- Registers are exposed through `const struct amdgpu_smuio_funcs smuio_v11_0_6_funcs`, which lets the wider AMDGPU device code locate ROM index/data registers and control ROM memory clock gating for this SMUIO IP revision.

## Risks and Edge Cases

- A wrong base index or offset makes SOC15 MMIO access hit a different register. For ROM access this can break VBIOS reads; for `CGTT_ROM_CLK_CTRL0` it can alter unrelated hardware state.
- `smuio_v11_0_6.c` intentionally skips ROM clock-gating control on APUs because the register is unavailable there. Reusing the offset macros without the same guard can fault or read undefined data on APU configurations.
- This 11.0.6 subset is narrower than the 11.0.0 and 13.0.2 maps. Code should not assume other SMUIO registers are available from this header.

## Test Signals

- Build coverage for `smuio_v11_0_6.c` validates the three exported offset names and matching mask names.
- Runtime VBIOS ROM reads validate `mmROM_INDEX`/`mmROM_DATA`.
- Clock-gating enable/disable tests validate the `mmCGTT_ROM_CLK_CTRL0` address and APU skip path.
- Comparing `SOC15_REG_OFFSET(SMUIO, 0, mm*)` output against hardware register documentation or known-good traces is the primary regression check for generated offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_6_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_6_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_6_sh_mask.h

## Purpose

`smuio_11_0_6_sh_mask.h` is the SMUIO 11.0.6 generated shift/mask header for the ROM clock-gating and ROM indexed access registers named by `smuio_11_0_6_offset.h`. It provides the field constants needed to safely update `CGTT_ROM_CLK_CTRL0` and interpret `ROM_INDEX`/`ROM_DATA`.

## Important APIs, Types, and Macros

The header exports preprocessor macros only:

- `CGTT_ROM_CLK_CTRL0__ON_DELAY__SHIFT` and `ON_DELAY_MASK` cover the low 4-bit on-delay field.
- `CGTT_ROM_CLK_CTRL0__OFF_HYSTERESIS__SHIFT` and `OFF_HYSTERESIS_MASK` cover bits 4..11.
- `CGTT_ROM_CLK_CTRL0__SOFT_OVERRIDE1__SHIFT` / `SOFT_OVERRIDE1_MASK` and `SOFT_OVERRIDE0__SHIFT` / `SOFT_OVERRIDE0_MASK` cover bits 30 and 31. These are the fields AMDGPU toggles for ROM MGCG enable/disable.
- `ROM_INDEX__ROM_INDEX__SHIFT` and `ROM_INDEX__ROM_INDEX_MASK` define a 25-bit ROM index field (`0x01ffffff`).
- `ROM_DATA__ROM_DATA__SHIFT` and `ROM_DATA__ROM_DATA_MASK` expose the full 32-bit ROM data window.

There are no functions, types, or storage objects.

## Control Flow

The header contains no control flow. Runtime behavior is in `amdgpu/smuio_v11_0_6.c`:

- Read `mmCGTT_ROM_CLK_CTRL0`.
- If enabling and `AMD_CG_SUPPORT_ROM_MGCG` is set, clear both `SOFT_OVERRIDE` bits so hardware clock gating can operate.
- Otherwise set both override bits to force ROM clocking behavior.
- Write back only when the value differs.
- Report ROM MGCG support when `SOFT_OVERRIDE0` is clear.

The `ROM_INDEX` and `ROM_DATA` masks are available for indexed ROM access, although the helper currently exposes offsets rather than doing explicit field extraction in this file's direct consumer.

## State and Persistence Behavior

The macros have no state. They describe persistent hardware fields:

- `SOFT_OVERRIDE0/1` hold clock-gating override configuration until changed or reset.
- `ON_DELAY` and `OFF_HYSTERESIS` are timing fields for ROM clock-gating transitions.
- `ROM_INDEX` and `ROM_DATA` are transient ROM access fields.

## Dependencies

This header must be used with the 11.0.6 offset header so masks are applied to the correct register addresses. Runtime consumers depend on AMDGPU's SOC15 MMIO helpers and clock-gating flags. The include guard is `_smuio_11_0_6_SH_MASK_HEADER`.

## Integration Points

Direct include:

- `drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.c`

The constants integrate into `smuio_v11_0_6_funcs`, where ROM offset discovery and ROM MGCG state/control are exposed to the wider AMDGPU device layer.

## Risks and Edge Cases

- The `ROM_INDEX` mask is 25 bits in 11.0.6, unlike the 24-bit mask in some older SMUIO maps. Sharing ROM index manipulation code across versions without the right header can truncate or overrun the address field.
- Inverting the meaning of the soft override bits would flip clock-gating behavior. The current consumer treats cleared override bits as enabled MGCG and set bits as disabled/forced override.
- The APU skip in the consumer is important because `CGTT_ROM_CLK_CTRL0` is not available for APUs.

## Test Signals

- Compile `smuio_v11_0_6.c` to catch missing field macros.
- Exercise ROM clock-gating transitions and inspect `CGTT_ROM_CLK_CTRL0` before and after enable/disable.
- Verify `get_clock_gating_state()` reports `AMD_CG_SUPPORT_ROM_MGCG` when `SOFT_OVERRIDE0` is clear.
- VBIOS ROM-read testing provides indirect coverage for the ROM index/data field sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_6_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_12_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_12_0_0_offset.h

## Purpose

`smuio_12_0_0_offset.h` is a generated offset header for the two SMUIO/PWR registers needed by SMU 12 GFXOFF power-state handling. It names the SMUIO GFX miscellaneous control register and a PWR miscellaneous control/status register with the base indexes required by SOC15 access helpers.

## Important APIs, Types, and Macros

The header exports macro constants only:

- `mmSMUIO_GFX_MISC_CNTL` at offset `0x00c8`, base index `0`.
- `mmPWR_MISC_CNTL_STATUS` at offset `0x0183`, base index `1`.

There are no functions, data types, or variables.

## Control Flow

No control flow exists in the header. Its primary direct consumer, `pm/swsmu/smu12/smu_v12_0.c`, uses `mmSMUIO_GFX_MISC_CNTL` in `smu_v12_0_get_gfxoff_status()`:

- Read `RREG32_SOC15(SMUIO, 0, mmSMUIO_GFX_MISC_CNTL)`.
- Mask with `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS_MASK`.
- Shift by `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS__SHIFT`.
- Return the two-bit GFXOFF status value where nearby comments document `0 = GFXOFF`, `1 = transition out`, `2 = not in GFXOFF`, and `3 = transition in`.

The `mmPWR_MISC_CNTL_STATUS` macro is explicitly undefined/redefined handling in the same source area because similarly named PWR-block headers exist; its base index matters when the register is accessed through SOC15 helpers.

## State and Persistence Behavior

The header has no state. It identifies hardware registers:

- `SMUIO_GFX_MISC_CNTL` exposes current GFXOFF status in SMUIO.
- `PWR_MISC_CNTL_STATUS` exposes PWR-side GFX RLC CGPG enable and GFXOFF status fields when paired with the mask header.

The values are live hardware status/control fields, not persisted by the driver.

## Dependencies

This header is meaningful with `smuio_12_0_0_sh_mask.h` and SOC15 register access macros. Its include guard is `_smuio_12_0_0_OFFSET_HEADER`. Runtime code depends on `struct smu_context`, `struct amdgpu_device`, `RREG32_SOC15`, and SMU message paths that allow or disallow GFXOFF.

## Integration Points

Direct include:

- `drivers/gpu/drm/amd/pm/swsmu/smu12/smu_v12_0.c`

Functional integration:

- `smu_v12_0_get_gfxoff_status()` reads `mmSMUIO_GFX_MISC_CNTL`.
- `smu_v12_0_gfx_off_control()` sends SMU messages to allow/disallow GFXOFF, making accurate status reads from this register important for power-management diagnostics and policy decisions.

## Risks and Edge Cases

- `mmPWR_MISC_CNTL_STATUS_BASE_IDX` is `1`, unlike the related PWR 10.0 offset header where similar names may use another base. Wrong include ordering or macro collision can target the wrong instance.
- The same field names exist in SMUIO and PWR-flavored headers. Consumers must pair offsets and masks from the same intended IP/register block.
- GFXOFF status is a moving hardware state; tests must tolerate transitional values `1` and `3`.

## Test Signals

- Build `smu_v12_0.c` with both offset and mask headers included.
- Runtime GFXOFF allow/disallow tests should observe plausible transitions through `smu_v12_0_get_gfxoff_status()`.
- Power-management debug output or tracepoints that sample GFXOFF can reveal incorrect offsets by returning stuck or impossible status values.
- Header-regeneration diffs should confirm offset `0x00c8`/base `0` and offset `0x0183`/base `1` remain aligned with hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_12_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_12_0_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_12_0_0_sh_mask.h

## Purpose

`smuio_12_0_0_sh_mask.h` is the generated bitfield companion for the SMUIO 12.0.0 GFXOFF-related registers. It defines masks and shifts used to extract GFXOFF status and, for the PWR status register, the GFX RLC CGPG enable bit.

## Important APIs, Types, and Macros

The header exports only macros:

- `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS_MASK` (`0x00000006`) and `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS__SHIFT` (`1`) extract the two-bit GFXOFF state from `mmSMUIO_GFX_MISC_CNTL`.
- `PWR_MISC_CNTL_STATUS__PWR_GFX_RLC_CGPG_EN__SHIFT` / `_MASK` cover bit 0 of `mmPWR_MISC_CNTL_STATUS`.
- `PWR_MISC_CNTL_STATUS__PWR_GFXOFF_STATUS__SHIFT` / `_MASK` cover bits 1..2 of the PWR-side status register.

No functions, structs, enums, or variables are declared.

## Control Flow

This header contains no logic. In direct consumer code:

- `smu_v12_0_get_gfxoff_status()` reads `mmSMUIO_GFX_MISC_CNTL`, masks with `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS_MASK`, shifts by `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS__SHIFT`, and returns a status enum-like integer.
- GFXOFF control itself is performed by SMU messages (`AllowGfxOff` and `DisallowGfxOff`); this header supplies status extraction constants used to observe the result.

## State and Persistence Behavior

The macros are stateless. They describe live hardware fields:

- `PWR_GFXOFF_STATUS` is volatile power-state status and can transition while being sampled.
- `PWR_GFX_RLC_CGPG_EN` is a control/status bit for graphics RLC coarse-grain power gating.

The driver does not persist values from this header. State is stored in hardware and firmware-controlled registers.

## Dependencies

The header should be used with `smuio_12_0_0_offset.h`. The include guard is `_smuio_12_0_0_SH_MASK_HEADER`. Runtime usage depends on AMDGPU PM/SMU code, SOC15 MMIO helpers, and SMU firmware responses to GFXOFF allow/disallow messages.

## Integration Points

Direct include:

- `drivers/gpu/drm/amd/pm/swsmu/smu12/smu_v12_0.c`

Related cross-version integration:

- Similar `PWR_GFXOFF_STATUS` fields exist in SMU10, SMU11, SMU13, and SMUIO 15 headers and board-specific PPT files. This header is the SMUIO 12.0.0 variant used by the SMU12 path.

## Risks and Edge Cases

- Because both SMUIO and PWR registers expose a `PWR_GFXOFF_STATUS` field, mixing the wrong offset and mask set can return plausible but incorrect values.
- Status values are two-bit state codes; callers should not treat any nonzero value as a simple boolean.
- The mask names overlap with other generated headers, so include ordering and `#undef` handling in consumers are part of the integration contract.

## Test Signals

- Compile-time validation from `smu_v12_0.c` confirms the mask names are available.
- Runtime GFXOFF tests should check all documented status codes are interpreted consistently: `0`, `1`, `2`, and `3`.
- Power-management suspend/resume and idle tests can catch stale status extraction if the mask or shift changes.
- Static comparison with generated register specs should verify `0x00000006` remains the correct status mask for both exposed registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_12_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_2_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_2_offset.h

## Purpose

`smuio_13_0_2_offset.h` is the generated SMUIO 13.0.2 register-offset map. It uses the newer `reg*` naming style and covers two address blocks: `smuio_smuio_SmuSmuioDec` at base `0x5a000` with base index `0`, and `smuio_smuio_pwr_SmuSmuioDec` at base `0x5a800` with base index `1`. The matching `smuio_13_0_2_sh_mask.h` supplies field masks.

## Important APIs, Types, and Macros

The header exports macros only. Major register groups:

- SVI and package topology: `regSMUSVI0_TEL_PLANE0`, `regSMUSVI0_PLANE0_CURRENTVID`, and `regSMUIO_MCM_CONFIG`.
- Two I2C controllers: `regCKSVII2C_*` and `regCKSVII2C1_*`, including control, target/source address, data command, timing counters, interrupt status/mask/raw/clear registers, FIFO levels, enable/status, abort source, DMA controls, SDA timing, spike length, and component identity registers.
- Reset and power management: `regSMUIO_MP_RESET_INTR`, `regSMUIO_SOC_HALT`, `regSMUIO_PWRMGT`, and `regSMUIO_GFX_MISC_CNTL`.
- ROM access/control: `regROM_CNTL`, `regPAGE_MIRROR_CNTL`, `regROM_STATUS`, `regCGTT_ROM_CLK_CTRL0`, `regROM_INDEX`, `regROM_DATA`, `regROM_START`, `regROM_SW_CNTL`, `regROM_SW_STATUS`, `regROM_SW_COMMAND`, and `regROM_SW_DATA_1` through `regROM_SW_DATA_64`.
- GPIO, pinstrap, and SMIO: `regSMU_GPIOPAD_*`, `regDFT_PINSTRAPS`, `regROM_CC_BIF_PINSTRAP`, `regIO_SMUIO_PINSTRAP`, `regSMUIO_PCC_*`, `regSMUIO_GPIO_INT*_SELECT`, `regSMU_GPIOPAD_MP_INT*_STAT`, `regSMIO_INDEX`, `regS0_VID_SMIO_CNTL`, `regS1_VID_SMIO_CNTL`, `regOPEN_DRAIN_SELECT`, and `regSMIO_ENABLE`.
- Power block at base index `1`: `regIP_DISCOVERY_VERSION`, `regSOC_GAP_PWROK`, `regGFX_GAP_PWROK`, `regPWROK_REFCLK_GAP_CYCLES`, golden TSC increment/count/shadow registers, `regSCRATCH_REGISTER0` through `regSCRATCH_REGISTER7`, display timer controls/debug registers, `regPWR_DISP_TIMER_GLOBAL_CONTROL`, and `regPWR_IH_CONTROL`.

There are no functions, structs, or variables.

## Control Flow

The header has no internal control flow. Runtime control appears in consumers:

- `amdgpu/smuio_v13_0.c` uses `regROM_INDEX`, `regROM_DATA`, and `regCGTT_ROM_CLK_CTRL0` to implement ROM access and ROM memory clock-gating control.
- `smuio_v13_0_update_rom_clock_gating()` reads `regCGTT_ROM_CLK_CTRL0`, clears or sets `CGTT_ROM_CLK_CTRL0__SOFT_OVERRIDE0_MASK` and `SOFT_OVERRIDE1_MASK`, and writes back when changed. It skips APUs.
- `smuio_v13_0_get_clock_gating_state()` reads the same register and reports ROM MGCG support when soft override bit 0 is clear.
- `smuio_v13_0_get_die_id()` and `smuio_v13_0_get_socket_id()` read `regSMUIO_MCM_CONFIG` and use matching masks to extract topology fields.
- `pm/swsmu/smu13/smu_v13_0.c` reads `regSMUSVI0_TEL_PLANE0` and extracts VDDCOR telemetry using the matching mask header.

## State and Persistence Behavior

This header does not store state. It maps names to hardware MMIO offsets:

- ROM clock-gating override state persists in `regCGTT_ROM_CLK_CTRL0`.
- ROM index/data and software ROM data registers provide transient firmware-image access.
- MCM configuration and pinstrap registers expose package/board identity, often latch-like hardware state.
- GPIO/SMIO registers configure pad drive, receive, pull-up/down, open-drain, Schmitt, SCL/SDA, interrupt, and routing behavior.
- Power-block TSC, scratch, power-good, and display timer registers are live hardware state; scratch registers can be used as small firmware/driver communication or diagnostic storage depending on platform policy.

## Dependencies

The include guard is `_smuio_13_0_2_OFFSET_HEADER`. The macros assume SOC15 register access infrastructure and must be paired with `smuio_13_0_2_sh_mask.h`. Consumers depend on `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, `amdgpu_device`, `AMD_IS_APU`, and clock-gating capability flags.

## Integration Points

Direct includes found in this tree:

- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c`
- `drivers/gpu/drm/amd/amdgpu/smuio_v13_0.c`

Representative integration:

- `smuio_v13_0_funcs` exposes ROM offset lookup, ROM clock-gating control, clock-gating state, die ID, and socket ID to the AMDGPU core.
- SMU13 PM code uses SVI telemetry offsets to read voltage information.
- Cross-version SMUIO files (`13_0_3`, `13_0_6`, `14_0_2`, `15_*`) show similar layouts with different offsets/base indexes, reinforcing that this header is version-specific.

## Risks and Edge Cases

- The 13.0.2 header uses `reg*` names, unlike older `mm*` headers. Mixing naming conventions or including the wrong IP revision can produce compile errors or, worse, valid access to the wrong register.
- Base index changes matter. Most SMUIO registers here use index `0`, while the power address block uses index `1`. Incorrect base index handling targets the wrong address block.
- The direct consumer skips ROM clock-gating registers on APUs. New users of `regCGTT_ROM_CLK_CTRL0` should preserve the same guard.
- Many GPIO and interrupt registers are side-effect prone. `CLR_*` and ack-style registers should be read/written only with hardware semantics in mind.
- The file includes `regSMUIO_GFX_MISC_CNTL` at `0x00d1`, while some board-specific SMU13 code hardcodes different offsets for related ASICs. Consumers must select the header matching the detected IP version.

## Test Signals

- Build coverage for `smuio_v13_0.c` and `smu_v13_0.c` validates core offset names.
- Runtime VBIOS read tests validate `regROM_INDEX` and `regROM_DATA`.
- ROM clock-gating tests validate `regCGTT_ROM_CLK_CTRL0` and soft override handling.
- Multi-die or socketed GPU tests validate `regSMUIO_MCM_CONFIG` extraction through die/socket helpers.
- SMU13 voltage telemetry tests validate `regSMUSVI0_TEL_PLANE0` alignment with its mask header.
- Hardware register trace comparison is useful for high-risk GPIO, pinstrap, display timer, and power-block offsets because many are not covered by common boot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_2_offset.h -->

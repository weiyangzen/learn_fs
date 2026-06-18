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

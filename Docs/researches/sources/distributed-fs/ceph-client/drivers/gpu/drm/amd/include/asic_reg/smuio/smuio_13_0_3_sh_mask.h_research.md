# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_3_sh_mask.h

## Purpose

`smuio_13_0_3_sh_mask.h` is the generated field-layout companion for `smuio_13_0_3_offset.h`. It exports masks and shifts for SMUIO 13.0.3 reset, TSC, software timer, miscellaneous/MCM, scratch, and GPIO registers. It contains no executable code; its purpose is to let AMDGPU consumers decode hardware fields without embedding raw bit positions.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or variables. The macro API follows the generated AMD pattern:

- `REGISTER__FIELD__SHIFT`
- `REGISTER__FIELD_MASK`

Major field groups include:

- Reset/halt: `SMUIO_MP_RESET_INTR__SMUIO_MP_RESET_INTR` and `SMUIO_SOC_HALT` watchdog force `PWROK`/`RESETn` enable fields.
- Power-good/TSC: `PWROK_REFCLK_GAP_CYCLES`, `GOLDEN_TSC_INCREMENT_*`, `GOLDEN_TSC_COUNT_*`, `SOC_GOLDEN_TSC_SHADOW_*`, and `SOC_GAP_PWROK`.
- Software timer and power interrupt handling: `PWR_VIRT_RESET_REQ` with VF/PF FLR bits, `PWR_DISP_TIMER_CONTROL`, `PWR_DISP_TIMER_DEBUG`, `PWR_DISP_TIMER2_CONTROL`, `PWR_DISP_TIMER2_DEBUG`, `PWR_DISP_TIMER_GLOBAL_CONTROL`, and `PWR_IH_CONTROL`.
- MCM and discovery: `SMUIO_MCM_CONFIG` fields for `DIE_ID`, `PKG_TYPE`, `SOCKET_ID`, `PKG_SUBTYPE`, `CONSOLE_K`, `CONSOLE_A`, and `TOPOLOGY_ID`; `IP_DISCOVERY_VERSION`; and eight full-width scratch pad fields.
- GPIO: `SMU_GPIOPAD_SW_INT_STAT`, mask/output/drive/enable/value/receiver/pull registers, `SMU_GPIOPAD_PINSTRAPS` bit fields 0 through 30, `DFT_PINSTRAPS`, interrupt status enable/status/ack/enable/type/polarity fields, PCC GPIO select, S0/S1/SCHMEN/SCL/SDA controls, interrupt select and MP interrupt status registers, `SMIO_INDEX`, VID SMIO controls, `OPEN_DRAIN_SELECT`, and `SMIO_ENABLE`.

## Control Flow And Data Flow

The header has no internal control flow. Its main observed data flow is in `amdgpu/smuio_v13_0_3.c`:

1. Read `regSMUIO_MCM_CONFIG` through `RREG32_SOC15(SMUIO, 0, regSMUIO_MCM_CONFIG)`.
2. Decode `DIE_ID`, `SOCKET_ID`, or `PKG_TYPE` with `REG_GET_FIELD(data, SMUIO_MCM_CONFIG, FIELD)`.
3. Map decoded package bits to `AMDGPU_PKG_TYPE_CEM`, `AMDGPU_PKG_TYPE_OAM`, `AMDGPU_PKG_TYPE_APU`, or `AMDGPU_PKG_TYPE_UNKNOWN`.
4. Publish those operations through `const struct amdgpu_smuio_funcs smuio_v13_0_3_funcs`.

Other potential flows are standard register programming flows for timer interrupts, virtual reset requests, GPIO interrupt configuration, and scratch register communication, but this header itself only provides the field constants.

## State And Persistence Behavior

No state is stored in the header. The fields describe state held by SMUIO hardware:

- MCM package identity and console/topology bits sampled or provided by boot firmware/MP1.
- Reset/halt watchdog force controls.
- Golden TSC increment/count/shadow registers and power-good gap bits.
- Virtual reset requests and display timer interrupt counters/status/ack/masking.
- Scratch registers that can persist as mailbox-like firmware/driver state.
- GPIO configuration, pinstrap, interrupt, PCC, and SMIO state.

Fields such as interrupt acknowledgement, virtual reset, and watchdog controls are potentially side-effecting when written. The mask names do not encode those access rules.

## Dependencies And Integration Points

Direct dependencies are only the preprocessor and compatible inclusion order. Runtime integration depends on:

- `smuio_13_0_3_offset.h` for register offsets.
- `amdgpu/smuio_v13_0_3.c` for MCM/package query functions.
- `amdgpu_smuio_funcs`, which is the SMUIO version abstraction used by AMDGPU.
- SOC15 and AMDGPU bitfield helpers such as `RREG32_SOC15()` and `REG_GET_FIELD()`.

The `SMUIO_MCM_CONFIG` layout differs from SMUIO 13.0.2 and 13.0.6. In 13.0.3, `DIE_ID` is two bits at shift 0, `PKG_TYPE` starts at shift 2, `SOCKET_ID` at shift 8, and topology starts at shift 18.

## Risks And Edge Cases

- Version mixing is the main risk. A consumer can compile with the wrong mask header and still produce plausible but incorrect package or socket values.
- `PKG_TYPE` is decoded in `smuio_v13_0_3.c` with an additional `PKG_TYPE_MASK` of `0x3`; reserved values map to unknown. If hardware exposes more than the expected low two bits, software intentionally ignores them.
- GPIO pinstrap and interrupt fields are dense bitmaps. Off-by-one shifts can affect a different pin or interrupt line.
- `PWR_VIRT_RESET_REQ` contains both VF and PF FLR fields. Accidental writes could request reset for the wrong function scope.
- Full-width scratch masks give no ownership model; callers need an external firmware/driver contract to avoid clobbering state.
- The generated macro names with repeated `MASK` suffixes, such as timer trigger mask fields, reflect hardware field names and should not be "cleaned up" manually.

## Test Signals

- Compile tests for `smuio_v13_0_3.c` and any ASIC configuration selecting `smuio_v13_0_3_funcs`.
- Runtime checks that die ID, socket ID, and package type decode correctly on known SMUIO 13.0.3 boards.
- Register dump comparison for `SMUIO_MCM_CONFIG`, timer, scratch, and GPIO fields against hardware documentation.
- Reset and FLR testing where `PWR_VIRT_RESET_REQ` is used.
- GPIO interrupt and pinstrap validation on board variants that rely on SMUIO GPIO routing.
- Regeneration diff checks against AMD's canonical SMUIO 13.0.3 mask definitions.

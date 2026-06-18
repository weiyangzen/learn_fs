# Research: subset-b-003424

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_2_sh_mask.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_3_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_3_offset.h

## Purpose

`smuio_13_0_3_offset.h` is a generated AMDGPU SMUIO 13.0.3 register-address header. It exports symbolic `reg*` register offsets and their corresponding `*_BASE_IDX` values for the SMUIO reset, TSC, software timer, miscellaneous, and GPIO address blocks. It contains no executable logic and must be paired with `smuio_13_0_3_sh_mask.h` for field-level access.

The address block comments show the underlying hardware block layout: reset at base `0x5a300`, TSC at `0x5a8a0`, software timer at `0x5ac70`, miscellaneous at `0x5a000`, and GPIO at `0x5a500`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or variables. The API is a flat macro list:

- `regNAME` gives the register's generated SOC15 register offset.
- `regNAME_BASE_IDX` gives the generated base-index selector used by SOC15 register helpers.

Major groups are:

- Reset block: `regSMUIO_MP_RESET_INTR` and `regSMUIO_SOC_HALT`, both with base index `1`.
- TSC/power-good block: `regPWROK_REFCLK_GAP_CYCLES`, `regGOLDEN_TSC_INCREMENT_UPPER/LOWER`, `regGOLDEN_TSC_COUNT_UPPER/LOWER`, `regSOC_GOLDEN_TSC_SHADOW_UPPER/LOWER`, and `regSOC_GAP_PWROK`, using base index `2`.
- Software timer block: `regPWR_VIRT_RESET_REQ`, `regPWR_DISP_TIMER_CONTROL`, `regPWR_DISP_TIMER_DEBUG`, second display timer control/debug registers, global display timer control, and `regPWR_IH_CONTROL`, also using base index `2`.
- Misc block: `regSMUIO_MCM_CONFIG` with base index `1`, plus `regIP_DISCOVERY_VERSION` and `regSCRATCH_REGISTER0` through `regSCRATCH_REGISTER7` with base index `2`.
- GPIO block: `regSMU_GPIOPAD_*`, `regDFT_PINSTRAPS`, GPIO interrupt status/ack/enable/type/polarity registers, PCC selection, SMIO registers, and GPIO interrupt select/status registers, using base index `1`.

## Control Flow And Data Flow

This header has no control flow. It supplies address data to consumers:

1. A consumer includes this offset file and `smuio_13_0_3_sh_mask.h`.
2. The consumer passes `reg*` names to SOC15 MMIO helpers, typically with block `SMUIO` and instance `0`.
3. The consumer decodes or encodes fields with the matching mask header.

The direct consumer in this tree is `amdgpu/smuio_v13_0_3.c`. That file reads `regSMUIO_MCM_CONFIG` with `RREG32_SOC15(SMUIO, 0, regSMUIO_MCM_CONFIG)` and decodes `DIE_ID`, `SOCKET_ID`, and `PKG_TYPE` fields using the matching mask definitions. The resulting functions populate `amdgpu_smuio_funcs` for this SMUIO version.

## State And Persistence Behavior

No software state is stored in the header. The addressed hardware registers hold state such as:

- Reset interrupt and SoC halt/watchdog force-enable state.
- Power-good timing, golden TSC increment/count/shadow state, and SoC power-good gap.
- Virtual reset requests, display timer interrupt counters/status/ack, and PWR interrupt-handler credit/trigger controls.
- MCM package identity/topology, IP discovery version, and scratch registers.
- GPIO pad direction/value/receiver/pull/strap/interrupt/SMIO/PCC state.

The base-index values are part of the address contract. A wrong base index can route an otherwise correct register name to the wrong MMIO aperture.

## Dependencies And Integration Points

This file depends only on preprocessor inclusion. Integration points are:

- `smuio_13_0_3_sh_mask.h`, which defines the fields for these offsets.
- `amdgpu/smuio_v13_0_3.c`, which uses `regSMUIO_MCM_CONFIG` for die/socket/package queries.
- SOC15 register helpers, especially `RREG32_SOC15()` and `REG_GET_FIELD()`.
- ASIC initialization code that selects `smuio_v13_0_3_funcs` for matching devices.

The header intentionally does not duplicate access semantics. Consumers must know which registers are read-only, write-one-to-clear, strap-derived, or side-effecting.

## Risks And Edge Cases

- The generated offsets are hardware ABI data. Off-by-one offsets or wrong base-index values can cause reads from unrelated SMUIO registers.
- `regSMUIO_MCM_CONFIG_BASE_IDX` is `1` for 13.0.3, while nearby versions can use different base indices. Reusing address code across versions without the generated base-index contract is risky.
- Some GPIO and interrupt acknowledge registers likely have side effects. The address header cannot express access type or write-clear behavior.
- Scratch registers are full-width and persistent across some firmware/driver flows; accidental reuse can conflict with firmware expectations.
- The file has no compile-time connection to the mask header beyond naming convention, so mismatched offset/mask versions can compile and still decode wrong fields.

## Test Signals

- Build AMDGPU with SMUIO 13.0.3 enabled to ensure all generated names used by `smuio_v13_0_3.c` resolve.
- Probe matching hardware and verify die ID, socket ID, and package type are stable and plausible.
- Compare register dumps for SMUIO MCM, TSC, timer, scratch, and GPIO blocks against expected offsets from AMD's register database.
- Exercise reset, suspend/resume, and SR-IOV/virtual reset paths if the platform uses `PWR_VIRT_RESET_REQ` or display timer interrupts.
- Run generation-diff checks against canonical SMUIO 13.0.3 headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_3_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_3_sh_mask.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_3_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_6_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_6_offset.h

## Purpose

`smuio_13_0_6_offset.h` is a generated AMDGPU SMUIO 13.0.6 register-address header. It exports `reg*` offsets and `*_BASE_IDX` selector values for reset, TSC, software timer, miscellaneous, two CKSVII2C controller instances, power-management, ROM, ROM software-command payload, and GPIO blocks. It contains no executable logic and is intended to be used with `smuio_13_0_6_sh_mask.h`.

The visible hardware base comments place reset at `0x5a300`, TSC at `0x5a8a0`, software timer at `0x5ac70`, misc at `0x5a000`, I2C at `0x5a100`, ROM at `0x5a380`, and GPIO at `0x5a500`.

## Important APIs, Types, And Macros

There are no C functions, types, or variables. The API is the macro set:

- `regNAME`: generated register offset.
- `regNAME_BASE_IDX`: generated base-index selector for SOC15 helpers.

Important groups include:

- Reset and halt: `regSMUIO_MP_RESET_INTR`, `regSMUIO_SOC_HALT`.
- TSC/power-good: `regPWROK_REFCLK_GAP_CYCLES`, `regGOLDEN_TSC_INCREMENT_*`, `regGOLDEN_TSC_COUNT_*`, `regSOC_GOLDEN_TSC_SHADOW_*`, `regSOC_GAP_PWROK`.
- Software timer: display timer control/debug pairs, display timer global control, and `regPWR_IH_CONTROL`. Unlike 13.0.3, this offset header does not list `regPWR_VIRT_RESET_REQ` in the swtimer block.
- Misc: `regSMUIO_MCM_CONFIG`, `regIP_DISCOVERY_VERSION`, and `regSCRATCH_REGISTER0` through `regSCRATCH_REGISTER7`.
- I2C: full CKSVII2C and CKSVII2C1 register sets from control/target/data/timing/interrupt/FIFO/enable/status through component parameter/version/type registers, plus `regSMUIO_PWRMGT`.
- ROM: `regROM_CNTL`, `regPAGE_MIRROR_CNTL`, `regROM_STATUS`, `regCGTT_ROM_CLK_CTRL0`, `regROM_INDEX`, `regROM_DATA`, `regROM_START`, `regROM_SW_CNTL`, `regROM_SW_STATUS`, `regROM_SW_COMMAND`, and `regROM_SW_DATA_1` through `regROM_SW_DATA_64`.
- GPIO: `regSMU_GPIOPAD_*`, `regDFT_PINSTRAPS`, interrupt status/ack/enable/type/polarity, PCC selection, S0/S1/SCHMEN/SCL/SDA, interrupt select/status, `regSMIO_INDEX`, VID SMIO controls, `regOPEN_DRAIN_SELECT`, and `regSMIO_ENABLE`.

Most `*_BASE_IDX` values are `0` for reset, misc MCM, I2C, ROM, and GPIO, while TSC, swtimer, IP discovery, and scratch registers use base index `1`.

## Control Flow And Data Flow

The header has no runtime control flow. Consumers use it as address data:

1. Include this file and `smuio_13_0_6_sh_mask.h`.
2. Select offsets such as `regROM_INDEX`, `regROM_DATA`, or `regSMUIO_MCM_CONFIG`.
3. Pass them to SOC15 helpers such as `SOC15_REG_OFFSET()` or MMIO read/write helpers.
4. Decode or compose field values with the matching mask header.

Direct consumers visible in the tree include `amdgpu/smuio_v13_0_6.c`, which exposes `regROM_INDEX` and `regROM_DATA` through `amdgpu_smuio_funcs`, and `amdgpu/gfx_v11_0.c`, which includes the 13.0.6 SMUIO offset and mask headers alongside GFX 11.0 register headers. The latter makes SMUIO 13.0.6 register addresses available to GFX 11.0 flows that need shared timing or SMUIO state.

## State And Persistence Behavior

The file itself has no state. The addressed registers hold hardware state, including:

- Reset/halt and power-good/TSC state.
- Scratch registers and IP discovery version.
- Two I2C controller instances with timing, FIFO, interrupt, enable, and component-identification state.
- ROM index/data, SPI timing/control, busy status, page mirror, software-command payload and completion state.
- GPIO pad, strap, interrupt, PCC, open-drain, and SMIO state.

Register state persists in hardware across ordinary software reads/writes and may be reinitialized by reset, firmware, strap sampling, or power transitions. Base-index values are part of the persistent addressing contract used by SOC15 helpers.

## Dependencies And Integration Points

This file depends only on the C preprocessor. Practical integration points are:

- `smuio_13_0_6_sh_mask.h` for field masks and shifts.
- `amdgpu/smuio_v13_0_6.c`, which uses `regROM_INDEX` and `regROM_DATA`.
- `amdgpu/gfx_v11_0.c`, which includes the SMUIO 13.0.6 generated headers.
- AMDGPU SOC15 access helpers and the `amdgpu_smuio_funcs` abstraction.

The register set overlaps heavily with 13.0.2 but uses different base-index conventions and has its own generated address list. Consumers should not assume offsets from another SMUIO minor version are interchangeable.

## Risks And Edge Cases

- A wrong offset or base index can make a valid register name access the wrong SMUIO aperture. This is especially relevant because 13.0.3 uses different base-index values for similar blocks.
- The ROM data window contains many sequential software payload registers. Generation drift in the sequence can corrupt ROM command payloads or reads.
- I2C0 and I2C1 blocks are parallel and easy to confuse; using the wrong controller offset may program an inactive or board-specific bus.
- Address headers do not encode access semantics. ROM busy/done, GPIO interrupt ack, timer ack, and reset/halt registers may have side effects on read or write.
- `regPWR_DISP_TIMER_CONTROL` and `regROM_SW_DATA_50` both have numeric offset `0x011d` but belong to different base-index/address blocks. The base index and block context are therefore essential.
- Generated headers are not self-testing; semantic errors require hardware testing or generator/database comparison.

## Test Signals

- Compile AMDGPU configurations that include `smuio_v13_0_6.c` and `gfx_v11_0.c`.
- Verify VBIOS/ROM reads through the SMUIO function table on matching 13.0.6 devices.
- Run GFX 11.0 initialization, suspend/resume, and reset tests that include SMUIO 13.0.6 headers.
- Compare SMUIO register dumps against expected offsets and base indices for reset, TSC, I2C, ROM, and GPIO blocks.
- Exercise I2C and GPIO paths on boards where those SMUIO facilities are routed and enabled.
- Regenerate from AMD register sources and diff offsets/base indices against this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_13_0_6_offset.h -->

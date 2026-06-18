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

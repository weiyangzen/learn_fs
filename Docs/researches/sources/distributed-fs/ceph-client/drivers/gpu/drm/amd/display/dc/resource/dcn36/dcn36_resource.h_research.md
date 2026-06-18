# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.h

## Purpose

`dcn36_resource.h` exposes the DCN 3.6 resource-pool constructor and generation wrapper, plus a DCN36-specific HWSEQ register-list macro used by the C file to initialize `struct dce_hwseq_registers`.

## Important APIs, Types, And Functions

- `extern struct _vcs_dpi_ip_params_st dcn3_6_ip` and `extern struct _vcs_dpi_soc_bounding_box_st dcn3_6_soc`: DCN36 DML IP/SOC inputs.
- `TO_DCN36_RES_POOL(pool)`: converts a generic `struct resource_pool *` to `struct dcn36_resource_pool *`.
- `struct dcn36_resource_pool`: wrapper around `struct resource_pool base`.
- `dcn36_create_resource_pool(init_data, dc)`: exported constructor implemented in `dcn36_resource.c`.
- `HWSEQ_DCN36_REG_LIST()`: enumerates HW sequencer register offsets for global timer, host VM, DIO/ODM/MMHUBBUB/DCCG power and clock controls, OTG pixel-rate controls, time-base divisors, DISPCLK change control, RBBMIF timeout controls, CRC controls, power-gating domains, AZALIA audio controls, HPO control, and DMU clock control.

## Control Flow

The header has no executable flow. `HWSEQ_DCN36_REG_LIST()` expands inside the implementation's `hwseq_reg_init()` path after `REG_STRUCT` and register accessor macros are configured.

## State And Persistence Behavior

The header defines no runtime storage. Its macros drive initialization of C-file static register tables and expose type declarations used by the resource pool.

## Dependencies And Integration Points

It depends on `core_types.h` and the register macro environment established by `dcn36_resource.c`. The HWSEQ macro integrates DCN36-specific register coverage with the shared DCE/DCN hardware sequencer object.

## Risks And Edge Cases

- `HWSEQ_DCN36_REG_LIST()` is macro-context dependent: it assumes `SR` and `SRII` are defined to write a `REG_STRUCT` of the correct type.
- Register coverage must stay in sync with `dce_hwseq_registers` fields and DCN36 power/clock gating requirements.
- The external DML declarations must match linked FPU/DML objects.

## Test Signals

- Build coverage catches missing registers or structure fields when HWSEQ definitions drift.
- Runtime power/clock-gating tests exercise whether the listed domains and gates are complete for DCN36.
- Resource-pool destruction tests indirectly validate `TO_DCN36_RES_POOL()`.

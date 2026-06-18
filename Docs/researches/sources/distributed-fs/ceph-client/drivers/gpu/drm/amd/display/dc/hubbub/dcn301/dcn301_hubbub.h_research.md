# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn301/dcn301_hubbub.h

## Purpose

`dcn301_hubbub.h` declares the DCN3.01 Hubbub register and field list. It extends the DCN3.0 list with HVM/DCHVM registers and exposes the `hubbub301_construct` constructor used by DCN3.01 resource construction.

## Important APIs, Types, And Functions

- `HUBBUB_REG_LIST_DCN301(id)` expands `HUBBUB_REG_LIST_DCN30(id)` and appends `HUBBUB_HVM_REG_LIST()`.
- `HUBBUB_MASK_SH_LIST_DCN301(mask_sh)` expands the DCN3.0 mask/shift list and adds HVM fields: `HOSTVM_INIT_REQ`, GPUVM return power request/force/status bits, HVM clock gate disable bits, transaction request/response clock-request modes, RIOMMU prefetch/power status, RIOMMU active, and host VM prefetch done.
- `hubbub301_construct(...)` is the generation constructor prototype.

## Control Flow

The header has no executable control flow. Its macros are expanded during register-table construction. The constructor declared here is called by ASIC resource setup, after which all operational flow uses the function table installed by `dcn301_hubbub.c`.

## State And Persistence Behavior

The header owns no state. Its field coverage enables later code to mutate DCHVM/HVM hardware state, especially host VM initialization, RIOMMU prefetch, GPUVM retention power behavior, and HVM clock gating. Those effects are hardware-register side effects, not persisted file state.

## Dependencies And Integration Points

It includes `dcn30/dcn30_hubbub.h`, inheriting the DCN3.0 register model. It integrates with register generation for DCN3.01 ASICs and with any inherited helper that needs HVM fields, such as DCHVM initialization or VM-related power management.

## Risks And Edge Cases

- HVM fields must exist in the ASIC register headers; otherwise macro expansion breaks the build.
- The constructor implementation chooses inherited DCN2.1/DCN3 callbacks, so this header must expose the exact extra HVM fields those callbacks expect.
- If a platform lacks HVM support but uses this register list, runtime code must avoid calling HVM-specific helpers or handle inactive RIOMMU status safely.

## Test Signals

Build coverage validates macro expansion. Runtime tests should check DCN3.01 VM aperture setup, host VM init requests, RIOMMU active/prefetch status transitions, and power/clock gating interactions when display init enables DCHVM paths.

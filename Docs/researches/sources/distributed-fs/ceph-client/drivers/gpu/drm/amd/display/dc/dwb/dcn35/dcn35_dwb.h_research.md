# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn35/dcn35_dwb.h

## Purpose

`dcn35_dwb.h` defines the DCN3.5 DWB extension over DCN30. It adds the FGCg repeat-disable field to the DWB register field list and declares construction/FGCg APIs.

## Important APIs, Types, And Functions

Key definitions are `DWBC_COMMON_MASK_SH_LIST_DCN35`, `DWBC_REG_FIELD_LIST_DCN3_5`, `struct dcn35_dwbc_mask`, `struct dcn35_dwbc_shift`, `dcn35_dwbc_construct`, and `dcn35_dwbc_set_fgcg`.

## Control Flow

The header has no execution flow. It extends the macro-expanded DCN30 field set with `DWB_FGCG_REP_DIS` so DCN35 source can reuse the base DWB object and programming code.

## State, Dependencies, Risks, And Test Signals

It defines metadata only. Runtime state persists in hardware registers and inherited `struct dcn30_dwbc`. It includes `resource.h`, `dwb.h`, and `dcn30/dcn30_dwb.h`. Risks include field-list layout mismatch and missing register definitions on some ASIC headers. Build coverage and FGCg register toggling tests are sufficient for this small adapter.

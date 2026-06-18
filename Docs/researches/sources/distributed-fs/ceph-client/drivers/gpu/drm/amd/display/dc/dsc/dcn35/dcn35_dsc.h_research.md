# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn35/dcn35_dsc.h

## Purpose

`dcn35_dsc.h` defines the DCN3.5 DSC register-field extension over DCN20. It adds the fine-grain clock-gating repeat disable field and declares DCN35 constructor and FGCg control APIs.

## Important APIs, Types, And Functions

Key definitions are `DSC_REG_LIST_SH_MASK_DCN35`, `DSC_FIELD_LIST_DCN35`, `struct dcn35_dsc_shift`, `struct dcn35_dsc_mask`, `dsc35_construct`, and `dsc35_set_fgcg`.

## Control Flow

The header itself has no runtime control flow. It expands DCN20 shift/mask lists with `DSC_FGCG_REP_DIS`, allowing `dcn35_dsc.c` to reuse DCN20 register structures and function implementations while reaching the additional DCN35 field through typed casts.

## State, Dependencies, Risks, And Test Signals

It defines static register metadata layout only. Runtime state is held by `struct dcn20_dsc` and hardware registers. It includes `dcn20/dcn20_dsc.h` and is consumed by DCN35 resource construction and power/clock-gating paths. Risks include structure layout mismatch and missing generated register definitions for `DSC_FGCG_REP_DIS`. Build tests and runtime FGCg toggle tests catch most issues.

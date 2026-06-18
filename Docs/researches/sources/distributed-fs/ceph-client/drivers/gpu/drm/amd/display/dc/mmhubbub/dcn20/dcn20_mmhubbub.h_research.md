# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h

Purpose: defines the DCN2.0 MMHUBBUB register map, field lists, object layout, and public helper prototypes.

Important APIs/types: `TO_DCN20_MMHUBBUB`, `MCIF_WB_COMMON_REG_LIST_DCN2_0`, `MCIF_WB_COMMON_MASK_SH_LIST_DCN2_0`, `MCIF_WB_REG_FIELD_LIST_DCN2_0`, and `MCIF_WB_REG_VARIABLE_LIST_DCN2_0` generate register/mask/shift structures. Defines `struct dcn20_mmhubbub_registers`, `mask`, `shift`, and `struct dcn20_mmhubbub`.

Control flow/integration: ASIC resource code provides concrete register lists and calls `dcn20_mmhubbub_construct`; function tables then expose MCIF operations through the generic `mcif_wb` base.

State/persistence: the object stores `mcif_wb` base plus const register/shift/mask pointers. Runtime hardware state is manipulated by functions in the `.c` file.

Dependencies: includes `mcif_wb` through the implementation and relies on register macro definitions such as `SRI`/`SF` from surrounding DCN resource code.

Risks: macro lists are long and tightly coupled to generated register headers. A missing field can break later code that conditionally checks masks, such as VCE slice interrupt support.

Test signals: compile-time construction for DCN2.0 resources, register list completeness, and writeback feature tests using every function pointer.

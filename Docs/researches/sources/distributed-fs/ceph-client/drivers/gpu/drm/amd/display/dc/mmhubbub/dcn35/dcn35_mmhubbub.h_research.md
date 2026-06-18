# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn35/dcn35_mmhubbub.h

Purpose: defines DCN3.5 MMHUBBUB register structures and FGC clock-gating API.

Important APIs/types: `MCIF_WB_REG_VARIABLE_LIST_DCN3_5` extends DCN3.0 variables with `MMHUBBUB_CLOCK_CNTL`; `MCIF_WB_COMMON_MASK_SH_LIST_DCN3_5` extends DCN32 fields with clock-control fields; `MCIF_WB_REG_FIELD_LIST_DCN3_5` wraps inherited fields and added clock fields. Defines DCN3.5 register/mask/shift structs and exports constructor plus `dcn35_mmhubbub_set_fgcg`.

Control flow/integration: resource code uses this header to instantiate a DCN3.5 MMHUBBUB object that reuses DCN32 functions while allowing generation-specific clock control.

State/persistence: metadata only; the associated runtime object is still `struct dcn30_mmhubbub`.

Dependencies: includes `mcif_wb` and DCN32 header.

Risks: the nested struct field-list macro differs from simple flat lists; consumers must use the matching DCN35 casts/macros. FGC disable polarity is inverted in implementation.

Test signals: compile-time register structure initialization and runtime FGC enable/disable register verification.

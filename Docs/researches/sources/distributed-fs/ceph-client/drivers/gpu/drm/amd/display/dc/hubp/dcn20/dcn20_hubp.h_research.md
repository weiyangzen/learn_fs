# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn20/dcn20_hubp.h

Purpose: declares the DCN2+ HUBP register and field model plus the DCN20 concrete object and exported helper APIs. It extends DCN10 with DMDATA, VMID, flip timing, triple-buffer, GSL, cursor0 register naming, and forward-compatible DCN21/DCN30/DCN32/DCN401/DCN42 fields.

Important APIs and types: `TO_DCN20_HUBP` casts to `struct dcn20_hubp`. `HUBP_REG_LIST_DCN2_COMMON` and `HUBP_REG_LIST_DCN20` define DCN2 register address sets. `HUBP_MASK_SH_LIST_DCN2_SHARE_COMMON`, `HUBP_MASK_SH_LIST_DCN2_COMMON`, and `HUBP_MASK_SH_LIST_DCN20` define field mappings. `DCN2_HUBP_REG_COMMON_VARIABLE_LIST`, `DCN21_HUBP_REG_COMMON_VARIABLE_LIST`, `DCN30_HUBP_REG_COMMON_VARIABLE_LIST`, and later lists extend the register struct for newer ASICs. `struct dcn_hubp2_registers`, `struct dcn_hubp2_shift`, and `struct dcn_hubp2_mask` intentionally include the broadest later-generation fields. `struct dcn20_hubp` embeds common `hubp`, state, and register metadata.

Control flow role: implementation files use this header to select generation-specific subsets from a common super-struct. DCN20 code consumes the DCN2 subset; DCN21 and DCN30 use the broader register/field lists while still storing pointers as `dcn_hubp2_*`.

State and persistence behavior: the header reuses `struct dcn_hubp_state` from DCN10 rather than defining a separate state object. Function prototypes expose persistent hardware features like triple buffering, DMDATA status, and register readback that higher layers invoke through `hubp_funcs`.

Dependencies and integration points: includes `../dcn10/dcn10_hubp.h`, so it is layered on top of the DCN1 register/state definitions. It is included by DCN20 C and later DCN generation implementations. Its forward declarations are used by resource code that constructs generation-specific HUBP instances.

Risks: because this header contains fields for multiple future generations, accidental use of a register absent on a given ASIC can compile but fail at runtime unless implementation checks `REG(field)`. Register and field lists must remain aligned with generated ASIC register headers. The super-struct approach increases coupling between old DCN20 code and later-generation additions.

Test signals: compile all ASIC variants that instantiate these lists, verify no missing initializers for DCN2/DCN21/DCN30 register tables, and exercise runtime paths that check optional registers. DMDATA, VMID, triple-buffer, GSL, and cursor field programming are key integration tests.

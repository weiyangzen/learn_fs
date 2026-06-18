# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn21/dcn21_hubp.h

Purpose: declares the DCN21 HUBP register/field additions and concrete object. DCN21 extends DCN2 common support with extra flip and vblank parameters for host-VM deadlines and a `VM_GROUP_SIZE` requestor field.

Important APIs and types: `TO_DCN21_HUBP` casts from common `hubp`. `HUBP_REG_LIST_DCN21` adds `FLIP_PARAMETERS_3` through `FLIP_PARAMETERS_6` and `VBLANK_PARAMETERS_5/6` on top of DCN2 common registers. `HUBP_MASK_SH_LIST_DCN21_COMMON` maps common DCN/share/VM/cursor/DMDATA/flip/GSL/VMID fields plus DCN21 host-VM deadline fields. `HUBP_MASK_SH_LIST_DCN21` adds RB alignment. `struct dcn21_hubp` embeds common HUBP state and register pointers plus `PLAT_54186_wa_chroma_addr_offset`. Prototypes expose construction, host-VM deadline workaround, deadline programming, and requestor programming.

Control flow role: this header lets `dcn21_hubp.c` and later DCN30 code use DCN21 requestor/deadline helpers with the correct field names. The `VM_GROUP_SIZE` mapping is central because requestor programming stores luma MPTE group size there instead of `MPTE_GROUP_SIZE`.

State and persistence behavior: the extra `PLAT_54186_wa_chroma_addr_offset` field is persistent object state reserved for a platform workaround, though the shown C implementation does not use it directly. Other state is inherited from `struct hubp` and `dcn_hubp_state`.

Dependencies and integration points: includes DCN20 and DCN10 headers. The exported DCN21 helpers are reused by DCN30 setup paths, so changes here affect multiple generations.

Risks: the broad common mask list combines DCN2 behavior with DCN21-only fields; wrong ASIC table use can access missing registers. The declared workaround state field can become stale or unused unless kept aligned with DMUB/platform workaround code. Requestor field naming differences are easy to regress in validation or readback.

Test signals: compile all DCN21 register table instantiations; runtime tests should confirm host-VM deadline registers, VM group requestor field, DMDATA status, GSL/triple-buffer, VMID, and cursor register mappings.

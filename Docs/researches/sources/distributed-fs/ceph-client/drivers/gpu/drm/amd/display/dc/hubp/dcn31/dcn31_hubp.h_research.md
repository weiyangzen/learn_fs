# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.h

Purpose: declares the DCN 3.1 HUBP register field set and public entry points. It extends the DCN 3.0 mask list with DCN 3.1 fields for unbounded requesting, soft reset, cursor request mode, and segment allocation error status.

Important APIs and definitions: `HUBP_MASK_SH_LIST_DCN31()` expands a full HUBP field list for generated register shift/mask tables. New or notable fields versus DCN 3.0 include `HUBP_UNBOUNDED_REQ_MODE`, `HUBP_SOFT_RESET`, `CURSOR_REQ_MODE`, and `HUBP_SEG_ALLOC_ERR_STATUS`. The header declares `hubp31_construct()`, `hubp31_soft_reset()`, `hubp31_set_unbounded_requesting()`, `hubp31_program_extended_blank_value()`, and `hubp31_get_det_config_error()`.

Control flow: no executable code is present, but the macro establishes the compile-time register contract consumed by DCN 3.1 resource files and by the implementation in `dcn31_hubp.c`. Later variants include this header to reuse DCN 3.1 function declarations and field coverage.

State and persistence: the exposed fields control persistent hardware state for request scheduling, reset, blank timing, cursor fetching, and DET allocation diagnostics. The public functions write or read those fields through `reg_helper` macros in the `.c` implementation.

Dependencies and integration points: includes DCN 2.0, DCN 2.1, and DCN 3.0 HUBP headers. It is used by `dcn32_hubp.h`, `dcn35_hubp.h`, `dcn401_hubp.h`, and `dcn42_hubp.h` either directly or indirectly, making it part of the shared DCN 3.x/4.x compatibility layer.

Risks and test signals: because this header duplicates a large field inventory, merge conflicts or register-spec changes can drop a needed field. Missing cursor or reset masks produce runtime register corruption rather than compile errors if table layouts still compile. Test signals are build warnings, generated register table validation, modeset with soft reset, cursor timing validation, DET allocation error injection/readback, and unbounded-request display scenarios.

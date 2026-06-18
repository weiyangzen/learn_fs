# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_rq_dlg_calc_314.h

Purpose: declares the DCN314 RQ/DLG register-calculation interface used by DML consumers and tests. It exposes one entry point for request-queue register extraction and one for DLG/TTU register extraction.

Important APIs/types/functions: includes `../display_rq_dlg_helpers.h` for `display_rq_regs_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, `display_pipe_params_st`, and `display_e2e_pipe_params_st`. It forward-declares `struct display_mode_lib`. Public functions are `dml314_rq_dlg_get_rq_reg(...)` and `dml314_rq_dlg_get_dlg_reg(...)`.

Control flow: this header has no executable flow. Callers pass a mode library, source or end-to-end pipe params, and output register structs. The DLG entry also carries pipe count/index plus policy booleans for cstate, pstate, VM, viewport-position ignoring, and immediate-flip support, even though the DCN314 implementation currently relies mostly on VBA getter state for those policy outcomes.

State and persistence: no state is declared. Outputs are written through caller-owned register structs by the implementation. Inputs are borrowed and must remain valid for the duration of calculation.

Dependencies and integration: guarded by `__DML314_DISPLAY_RQ_DLG_CALC_H__`. This header is part of the generation-specific DML callback surface and pairs with `display_rq_dlg_calc_314.c`. The comments identify `dml314_rq_dlg_get_rq_reg` as the main test entry for extracting register values.

Risks: ABI compatibility is important because resource code and tests call through these exact signatures. Boolean policy parameters can be misleading if future code expects them to directly drive all paths; the implementation presently marks several as unused in the lower-level DLG helper. Comments contain minor typos but no behavioral issue.

Test signals: compile coverage, unit-style RQ/DLG register extraction tests, and generation-specific DML validation that calls these functions for active pipe configurations.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.h

Purpose: declares DML2.0 RQ/DLG/TTU calculation entry points used to turn DML mode-programming results into hardware register structs.

Important APIs/types/functions: exports `dml_rq_dlg_get_rq_reg()`, `dml_rq_dlg_get_dlg_reg()`, and `dml_rq_dlg_get_arb_params()`. It forward-declares `struct display_mode_lib_st` and uses DML display register types from `display_mode_core_structs.h`.

Control flow: no direct flow. Comments document that callers must have already run mode programming before requesting register values.

State and persistence behavior: no header state. Functions fill caller-provided output structs.

Dependencies and integration points: included by `dml2_utils.c` and the implementation. It bridges DML core outputs to DC pipe register caches.

Risks and test signals: callers must pass the correct DML pipe index; otherwise RQ/DLG fields are copied to the wrong DC pipe. Build coverage should catch struct type drift between DML core and DC-facing register containers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.h -->

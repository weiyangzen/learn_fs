# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.c

Purpose: implements the DCN 3.1 HUBP specialization. It mostly reuses DCN 3.0 helpers while adding unbounded request mode, HUBP soft reset, optimized blank programming, DET segment allocation error readback, and DCN 3.1 function table construction.

Important APIs and functions: `hubp31_set_unbounded_requesting()` updates `HUBP_UNBOUNDED_REQ_MODE` and forces `CURSOR_REQ_MODE` to 1. `hubp31_soft_reset()` writes `HUBP_SOFT_RESET`. `hubp31_program_extended_blank_value()` exposes the static `hubp31_program_extended_blank()` wrapper for `MIN_DST_Y_NEXT_START`. `hubp31_get_det_config_error()` reads `HUBP_SEG_ALLOC_ERR_STATUS`. `hubp31_construct()` initializes the base object, register/shift/mask pointers, instance id, and function table.

Control flow: construction installs `dcn31_hubp_funcs`. Runtime calls arrive through `struct hubp_funcs`: surface flips and configs route to `hubp3_*`, cursor and dmdata logic largely route to DCN 2.x/3.0 helpers, while DCN 3.1 specific entries handle unbounded requesting, soft reset, extended blank, and DET error readback. The functions are thin hardware register transactions with no allocation or retry logic.

State and persistence: writes persist in HUBP registers until reprogrammed or reset. `hubp31_construct()` stores immutable register table pointers in `struct dcn20_hubp` and sets `opp_id` invalid plus `mpcc_id` to `0xf`. `hubp31_get_det_config_error()` is read-only diagnostic state. Cursor request mode is forced whenever unbounded requesting is toggled, which is an intentional side effect.

Dependencies and integration points: includes `dm_services.h`, `dce_calcs.h`, `reg_helper.h`, conversion helpers, and `dcn31_hubp.h`. It depends heavily on DCN 2.x and DCN 3.0 helper functions. Display resource code for DCN 3.1 constructs these objects and higher-level HWSS/plane programming accesses them through the function table.

Risks and test signals: incorrect function table wiring can silently regress inherited behavior. Soft reset and unbounded request mode affect live request scheduling, so misuse can cause blanking, fetch stalls, or cursor timing problems. DET error status only works if the header mask list matches the register spec. Signals include DCN 3.1 build coverage, modeset/flip tests, cursor tests, SubVP or unbounded-request paths, register readback for `HUBP_SEG_ALLOC_ERR_STATUS`, and underflow monitoring.

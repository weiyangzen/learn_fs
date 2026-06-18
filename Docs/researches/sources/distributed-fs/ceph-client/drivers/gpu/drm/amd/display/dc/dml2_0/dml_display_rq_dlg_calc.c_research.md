<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.c

Purpose: converts programmed DML mode results into display request queue, DLG, TTU, and arbitration register structures for DCN programming.

Important APIs/types/functions: exports `dml_rq_dlg_get_rq_reg()`, `dml_rq_dlg_get_dlg_reg()`, and `dml_rq_dlg_get_arb_params()`. Internal `is_dual_plane()` recognizes 420 and RGBE-alpha formats that require luma/chroma or alpha-plane handling.

Control flow: RQ calculation reads plane/source format, swizzle, chunk sizes, group sizes, DET size, row heights, swath heights, stored swath sizes, and phantom status from DML getters. It encodes register fields with log2/floor conversions and chooses DET chroma base split, including a fixed half-MALL split for phantom dual-plane pipes. DLG/TTU calculation reads timing, plane, hardware, ODM mode, prefetch, VM/PTE/meta delivery, cursor, and watermark-related values, adjusts hblank reference cycles for ODM combine position, writes fixed-point register fields, clamps selected VM/PTE/meta values, and asserts register width constraints.

State and persistence behavior: no persistent state. It zeroes caller-provided register structs and fills them from `display_mode_lib_st` cached mode-programming outputs.

Dependencies and integration points: depends on `display_mode_core.h`, `display_mode_util.h`, DML getter APIs, DML math helpers, and `dml_print` logging macros. Called by `dml2_calculate_rq_and_dlg_params()` before copying results into DC pipe contexts.

Risks and test signals: many fields rely on DML getters having valid data after `dml_mode_programming()`. Register-width asserts can fire for unusual timings, high refclk ratios, or unsupported scaling. The code assumes at most one cursor and contiguous DML pipe indexes for ODM combine. Test signals include linear and tiled surfaces, dual-plane formats, RGBE alpha, phantom SubVP pipes, ODM 2:1/4:1, interlace, cursor enabled/disabled, low htotal magic path, and clamp behavior near 13/17/23/24-bit register limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.c -->

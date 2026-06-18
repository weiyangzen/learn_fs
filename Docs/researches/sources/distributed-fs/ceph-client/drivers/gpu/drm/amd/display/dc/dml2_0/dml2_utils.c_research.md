<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.c

Purpose: provides DML2.0 utility routines for copying DML config arrays, deriving output/clock constraints, mapping DML pipe indexes back to DC pipes, calculating RQ/DLG params, extracting watermarks/writeback settings, applying DET buffer policy, and recognizing stereo timings.

Important APIs/types/functions: exports copy helpers for timing/plane/surface/output arrays, `dml2_util_get_maximum_odm_combine_for_output()`, `is_dp2p0_output_encoder()`, `is_dtbclk_required()`, `dml2_copy_clocks_to_dc_state()`, `dml2_helper_find_dml_pipe_idx_by_stream_id()`, `dml2_calculate_rq_and_dlg_params()`, `dml2_extract_watermark_set()`, `dml2_calc_max_scaled_time()`, `dml2_extract_writeback_wm()`, `dml2_initialize_det_scratch()`, `dml2_apply_det_buffer_allocation_policy()`, `dml2_verify_det_buffer_configuration()`, and `dml2_is_stereo_timing()`.

Control flow: the most important path is `dml2_calculate_rq_and_dlg_params()`: it updates deep-sleep/fclk support, clamps dispclk to debug minimum, resolves each DC pipe to a DML pipe through stream or plane id mappings, populates DLG params, applies phantom-pipe DET/unbounded-request rules, reads DPPCLK/DET/MALL sizes from DML, calls RQ/DLG calculators, and copies register values into the output resource context. DET policy splits the available DET pool across streams, planes, and DPPs per surface, then verification triggers recalculation when DML allocates more than the hardware total.

State and persistence behavior: mutates `dc_state->bw_ctx`, `pipe_ctx` register caches, MALL size counters, DET helper scratch, and DML display config overrides. It does not keep independent static state.

Dependencies and integration points: depends on DML getters, `dml_display_rq_dlg_calc`, DC pipe/resource structs, DP2 HPO encoder fields, writeback structures, and mapping tables populated by `dml2_translation_helper.c` and `dml2_wrapper_fpu.c`.

Risks and test signals: DML/DC pipe index mismatches can write registers or DET sizes to the wrong pipe. `dml2_extract_writeback_wm()` iterates DMB slots and references `pipe_ctx[i].stream`, so writeback-only or sparse pipe layouts need coverage. DET rounding masks with `~0x3F`, assuming 64 KB segment alignment. Test signals include DP2 `dtbclk_en`, phantom DET zeroing, MALL size accounting, RQ/DLG register population, DET recalculation, writeback watermark extraction, and forced clock/debug minimum interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.c -->

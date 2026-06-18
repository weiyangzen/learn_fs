<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.c

## Purpose

`dc_spl.c` is the core scaler programming library. It converts high-level plane, stream, slicing, rotation, pixel-format, scaling-quality, EASF, and iSHARP inputs into `dscl_prog_data` for DCN scaler hardware programming.

## Important APIs, Types, And Functions

- Public APIs: `SPL_NAMESPACE(spl_calculate_scaler_params)` and `SPL_NAMESPACE(spl_get_number_of_taps)`.
- Geometry helpers: `calculate_plane_rec_in_timing_active`, `calculate_mpc_slice_in_timing_active`, `calculate_odm_slice_in_timing_active`, `spl_calculate_recout`, `intersect_rec`, and `shift_rec`.
- Scaling math: `spl_calculate_scaling_ratios`, `spl_calculate_viewport_size`, `spl_calculate_init_and_vp`, `spl_calculate_inits_and_viewports`, and `spl_handle_3d_recout`.
- Policy helpers: `spl_get_optimal_number_of_taps`, `enable_easf`, `spl_get_isharp_en`, `spl_get_dscl_mode`, and `spl_choose_lls_policy`.
- Programming emitters: `spl_set_dscl_prog_data`, `spl_set_easf_data`, `spl_set_isharp_data`, `spl_set_manual_ratio_init_data`, and `spl_set_taps_data`.

## Control Flow

The full parameter path zeroes scratch state, records active timing size, computes recout by mapping plane clip from stream-source to timing-active space, slices it by MPC and ODM, computes luma/chroma ratios, applies OPP recout adjustment, estimates viewport size, chooses taps/EASF/iSHARP using input policy and line-buffer callback limits, computes final viewport offsets and filter inits, handles stereo offsets, clamps viewport size, writes DSCL programming fields, then fills EASF and iSHARP-specific registers/LUT pointers.

`spl_get_number_of_taps` follows the same early path but only emits tap fields. This lets callers ask resource questions without filling the whole DSCL programming payload.

## State And Persistence Behavior

The function keeps all intermediate state in stack `struct spl_scratch` and writes caller-owned `spl_out->dscl_prog_data`. It mutates `spl_in->lls_pref` when the caller leaves it as `LLS_PREF_DONT_CARE`. Filter/LUT pointers refer to static tables in sibling files.

## Dependencies And Integration Points

It depends on `dc_spl_types.h`, fixed-point helpers, `dc_spl_scl_easf_filters.h`, `dc_spl_isharp_filters.h`, and SPL callback `spl_calc_lb_num_partitions`. DCN resource code enables SPL via `dc->config.use_spl` and uses the output to program DSCL, EASF, iSHARP, scaler filters, viewport, recout, black color, ratios, and inits.

## Risks And Edge Cases

- Many divisions assume nonzero source/destination dimensions and slice counts.
- `enable_easf` returns a variable named `skip_easf`, so misuse is easy when editing.
- Some paths fill DSCL data before returning false; callers must respect the boolean.
- Rotation, mirroring, chroma cositing, 3D, MPC slicing, ODM slicing, custom width, and OPP adjustments interact tightly.
- EASF and iSHARP only support certain tap combinations; policy/tap changes can silently disable features.
- The line-buffer callback must be valid and return accurate partition counts.

## Test Signals

Strong test coverage includes identity scale bypass, RGB/YUV420/YUV444 formats, chroma cositing, 90/180/270 rotation, horizontal mirror, integer scaling, >2:1 EASF disable, >6:1 downscale asserts, MPO/MPC slicing, ODM combine, 3D side-by-side/top-bottom, line-buffer-limited vtaps, EASF linear/nonlinear modes, HDR coefficient calculation, and iSHARP policy thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl.c -->

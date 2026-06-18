# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc_dpi.c

## Purpose

`rc_calc_dpi.c` implements the DSCC parameter computation declared in `dscc_types.h`. It combines an input DRM DSC PPS with AMD RC parameters, calls the DRM DSC helper to finish RC/PPS derivation, and returns register-facing DSC parameters such as bytes-per-pixel and RC buffer model size.

## Important APIs, Types, And Functions

The exported function is `dscc_compute_dsc_parameters`. Private helpers are `copy_pps_fields`, which copies the subset of `struct drm_dsc_config` fields this path preserves, and `copy_rc_to_cfg`, which maps `struct rc_params` into DRM PPS RC fields.

## Control Flow

`dscc_compute_dsc_parameters` starts by copying the input PPS into `dsc_params->pps`, computes `initial_scale_value` from RC model size and initial fullness offset, copies the PPS into a temporary `drm_dsc_config`, overlays RC fields, chooses mux word size from bits-per-component, calls `drm_dsc_compute_rc_parameters`, computes `bytes_per_pixel` in u3.28 format by rounding `slice_chunk_size / slice_width`, copies the computed PPS back, and stores `rc_bits` as the register RC buffer model size.

## State, Dependencies, Risks, And Test Signals

All data is temporary or caller-owned. It has no static state, no register access, and no persistence. It depends on DRM DSC helpers, `dscc_types.h`, and `rc_calc.h` for `struct rc_params`. Risks include division by `rc_model_size - initial_fullness_offset`, truncating 8-bit signed BPG offsets to 6-bit fields, array size assumptions around `QP_SET_SIZE`, mux word size thresholds, and callers treating a nonzero DRM helper return as success. Tests should validate computed PPS, bytes-per-pixel rounding, RC buffer model size, threshold/range propagation, and error handling for invalid PPS/RC inputs.

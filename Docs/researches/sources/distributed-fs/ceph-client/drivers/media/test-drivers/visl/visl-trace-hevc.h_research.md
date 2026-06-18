# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-hevc.h

## Purpose
`visl-trace-hevc.h` defines tracepoints for HEVC stateless V4L2 controls, reference picture sets, prediction weights, and DPB entries.

## Important APIs, types, and functions
The trace system is `visl_hevc_controls`. Event classes cover HEVC SPS, PPS, slice parameters, prediction weight tables, scaling matrices, decode parameters, long-term RPS extension, short-term RPS extension, and DPB entries. Defined events include `v4l2_ctrl_hevc_sps`, `v4l2_ctrl_hevc_pps`, `v4l2_ctrl_hevc_slice_params`, `v4l2_hevc_pred_weight_table`, `v4l2_ctrl_hevc_scaling_matrix`, `v4l2_ctrl_hevc_decode_params`, `v4l2_ctrl_hevc_ext_sps_lt_rps`, `v4l2_ctrl_hevc_ext_sps_st_rps`, and `v4l2_hevc_dpb_entry`.

The print logic decodes many HEVC flags and arrays: SPS/PPS feature flags, slice reference indices, weighted prediction arrays, scaling lists, decode POC sets, RPS fields, DPB timestamps, and long-term-reference flags.

## Control flow
`visl_trace_ctrls()` invokes these trace events for HEVC jobs after request controls are applied. The header is instantiated only through `visl-trace-points.c`.

## State and persistence
The tracepoints copy submitted control payloads and do not maintain any decoder state. Persistence is entirely in the kernel trace buffer.

## Dependencies and integration points
It depends on `linux/v4l2-controls.h`, `linux/tracepoint.h`, V4L2 HEVC stateless definitions, and VISL's trace include path. It integrates with the HEVC control descriptors in `visl-core.c` and the `visl_hevc_run` union in `visl-dec.h`.

## Risks and test signals
HEVC has large nested control data, so trace volume and field drift are the main risks. Tests should build with tracing enabled and run HEVC stateless requests that include slice params, decode params, RPS controls, and DPB entries, confirming all event printers compile and produce readable output.

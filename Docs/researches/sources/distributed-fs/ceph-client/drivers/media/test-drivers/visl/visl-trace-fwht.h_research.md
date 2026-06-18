# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-fwht.h

## Purpose
`visl-trace-fwht.h` defines the VISL tracepoint for the FWHT stateless parameter control.

## Important APIs, types, and functions
It sets `TRACE_SYSTEM` to `visl_fwht_controls` and declares `v4l2_ctrl_fwht_params_tmpl`, instantiated as `v4l2_ctrl_fwht_params`. The event stores individual FWHT fields: backward reference timestamp, version, width, height, flags, colorspace, transfer function, YCbCr encoding, and quantization. FWHT flags are decoded with `__print_flags()`.

## Control flow
`visl_trace_ctrls()` calls `trace_v4l2_ctrl_fwht_params()` when the current codec is `VISL_CODEC_FWHT`. `visl-trace-points.c` provides the single translation unit that creates the tracepoint symbols.

## State and persistence
No driver state is changed. The tracepoint snapshots a control payload for kernel tracing.

## Dependencies and integration points
It depends on the V4L2 FWHT control struct and the kernel tracepoint macro system. Its integration point is the decode trace dispatch in `visl-dec.c`.

## Risks and test signals
The tracepoint is small, so the main risk is field drift if the FWHT control changes. Test signals are successful module build and ftrace output showing FWHT parameters during FWHT stateless requests.

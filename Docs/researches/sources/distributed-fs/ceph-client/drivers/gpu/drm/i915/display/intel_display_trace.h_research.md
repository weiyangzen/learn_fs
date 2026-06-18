# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_trace.h

## Purpose
This header defines display trace events for pipe enable/disable, flips, CRCs, FIFO underruns, memory self-refresh/watermarks, plane/scaler updates, FBC transitions, vblank work, pipe update timing, and frontbuffer invalidate/flush. It supports both i915 and Xe trace namespaces by selecting `TRACE_SYSTEM` at preprocessing time.

## Important APIs, Types, and Functions
The exported tracepoints are `intel_pipe_enable`, `intel_pipe_disable`, `intel_crtc_flip_done`, `intel_pipe_crc`, `intel_cpu_fifo_underrun`, `intel_pch_fifo_underrun`, `intel_memory_cxsr`, `g4x_wm`, `vlv_wm`, `vlv_fifo_size`, `intel_plane_async_flip`, `intel_plane_update_noarm`, `intel_plane_update_arm`, `intel_plane_disable_arm`, `intel_plane_scaler_update_arm`, `intel_pipe_scaler_update_arm`, `intel_scaler_disable_arm`, `intel_fbc_activate`, `intel_fbc_deactivate`, `intel_fbc_nuke`, `intel_crtc_vblank_work_start`, `intel_crtc_vblank_work_end`, `intel_pipe_update_start`, `intel_pipe_update_vblank_evaded`, `intel_pipe_update_end`, `intel_frontbuffer_invalidate`, and `intel_frontbuffer_flush`. Helper macros include device-name extraction and fixed pipe frame/scanline formatting with static assertions for pipe numbering.

## Control Flow
Each tracepoint uses trace event fast-assign code to sample current frame and scanline counters, pipe names, rectangles, formats, watermark fields, or frontbuffer bits at the call site. The header finishes by setting `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` and including `<trace/define_trace.h>` outside the include guard, as required by Linux tracepoint generation.

## State and Persistence Behavior
Trace events do not own driver state. They snapshot selected fields into trace buffers when enabled. Several events sample live CRTC vblank counters and scanlines, so the recorded values are time-sensitive diagnostics rather than persistent driver state.

## Dependencies and Integration Points
It depends on Linux tracepoints, string helpers, `intel_crtc`, display core/limits/types, and vblank helpers. It integrates with display modeset, plane update, watermark, FBC, frontbuffer, underrun, and debugging paths. The i915/Xe `TRACE_SYSTEM` selection controls where events appear in tracing.

## Risks
Tracepoint fast paths must avoid expensive or unsafe operations when enabled in timing-sensitive display paths. Constant pipe formatting assumes `I915_MAX_PIPES` and pipe enum values remain aligned with the static assertions. Tracepoint field layouts are user-visible through tracing format files, so renaming fields or changing types can break tools. Some tracepoints dereference plane/framebuffer state and require valid call-site invariants.

## Test Signals
Signals include successful tracepoint compilation, visible events in ftrace/perf, enabling each event during modesets and flips, no crashes with tracing enabled, expected frame/scanline values, and trace output matching watermarks, scaler rectangles, FBC transitions, and frontbuffer bits.

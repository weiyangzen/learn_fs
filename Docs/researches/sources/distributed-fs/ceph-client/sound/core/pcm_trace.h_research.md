# sources/distributed-fs/ceph-client/sound/core/pcm_trace.h

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_trace.h` declares ALSA PCM runtime tracepoints used mainly for XRUN and hardware/application pointer debugging. It captures hardware pointer positions, XRUN events, pointer error reasons, and application pointer movement. The source was read as a complete 149-line file for this report.

## Important APIs, Types, and Functions

The header defines `TRACE_SYSTEM snd_pcm`, `TRACE_INCLUDE_FILE pcm_trace`, and four trace events: `hwptr`, `xrun`, `hw_ptr_error`, and `applptr`. The events capture card/device/substream identifiers, stream direction, pointer positions, period and buffer sizes, current `hw_ptr_base`, availability, and string reasons for hardware pointer errors.

## Control Flow

There is no standalone algorithm. When `CONFIG_SND_PCM_XRUN_DEBUG` causes `pcm_lib.c` to define `CREATE_TRACE_POINTS`, the trace events are generated and invoked from hardware-pointer update, XRUN handling, hardware pointer anomaly reporting, and application-pointer update paths. Without that config, `pcm_lib.c` compiles trace calls to no-ops.

## State and Persistence Behavior

The header does not own state. It snapshots selected runtime fields into the kernel tracing ring buffer when events are enabled. Captured trace records are transient diagnostic data and do not affect PCM runtime state.

## Dependencies and Integration Points

It depends on Linux tracepoint infrastructure and ALSA PCM runtime structures. Integration is almost entirely with `pcm_lib.c`: `trace_hwptr()` is called after driver pointer sampling and alignment, `trace_xrun()` is called from `__snd_pcm_xrun()`, `trace_hw_ptr_error()` is called on pointer anomalies, and `trace_applptr()` is called from `pcm_lib_apply_appl_ptr()`.

## Risks and Edge Cases

Tracepoints dereference runtime/control/status fields, so call sites must only fire while the stream runtime is valid and locked appropriately. Field names and formats are part of diagnostic tooling expectations. Pointer values can wrap at `runtime->boundary`, so consumers must interpret them with buffer and period sizes. Enabling these events on busy streams can generate high event volume.

## Test Signals

Build with `CONFIG_SND_PCM_XRUN_DEBUG`, enable `snd_pcm:hwptr`, `snd_pcm:xrun`, `snd_pcm:hw_ptr_error`, and `snd_pcm:applptr` through ftrace/perf, then run playback/capture with normal period interrupts, forced XRUN, application pointer rewinds/forwards, and invalid pointer simulation from a test driver. Verify event fields match stream identity and runtime pointer state.

# sources/distributed-fs/ceph-client/sound/hda/common/controller_trace.h

## Purpose
Defines Linux tracepoints for common HD-audio controller PCM operations and position reporting. The tracepoints give low-overhead visibility into stream lifecycle, trigger commands, and DMA position/delay accounting.

## Important APIs, Types, And Functions
Declares `TRACE_EVENT(azx_pcm_trigger)`, `TRACE_EVENT(azx_get_position)`, and an `azx_pcm` event class used by `azx_pcm_open`, `azx_pcm_close`, `azx_pcm_hw_params`, and `azx_pcm_prepare`. Event payloads include card number, stream index, trigger command, stream tag, position, and delay.

## Control Flow
`controller.c` defines `CREATE_TRACE_POINTS` and includes this header, causing the tracepoint definitions to be emitted. PCM ops call the generated `trace_azx_*` helpers at open, close, hw_params, prepare, trigger, and position-read points.

## State And Persistence Behavior
This header persists no driver state. It publishes snapshots from `struct azx` and `struct azx_dev` into ftrace/perf buffers when tracing is enabled.

## Dependencies And Integration Points
Depends on Linux tracepoint infrastructure, forward declarations for `struct azx` and `struct azx_dev`, and must remain outside normal include protection for `trace/define_trace.h` generation. Users consume events through ftrace, perf, trace-cmd, or kernel tracing tools.

## Risks And Test Signals
Risks are compile-time trace macro breakage, include-path mistakes, or dereferencing fields that are invalid at a trace call site. Test signals are successful build with tracing enabled and visible `hda_controller:*` events during PCM operations.

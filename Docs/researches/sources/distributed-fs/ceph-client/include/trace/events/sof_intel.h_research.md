
# sources/distributed-fs/ceph-client/include/trace/events/sof_intel.h

## Purpose
Defines Intel-specific SOF tracepoints for HDA IRQs, IPC firmware doorbell direction, D0I3C updates, IPC checks, DSP PCM stream binding, stream status, and stream IRQ checks.

## Important APIs, Types, and Functions
Events include `sof_intel_hda_irq`, `sof_intel_ipc_firmware_response`, `sof_intel_ipc_firmware_initiated`, `sof_intel_D0I3C_updated`, `sof_intel_hda_irq_ipc_check`, `sof_intel_hda_dsp_pcm`, `sof_intel_hda_dsp_stream_status`, and `sof_intel_hda_dsp_check_stream_irq`. The IPC firmware template captures header and extension registers; stream events capture stream tags, channel maps, positions, status, and IRQ metadata.

## Control Flow
Intel HDA/SOF driver code emits IRQ traces when interrupts arrive, IPC traces around firmware-originated or host-originated messages, D0I3C traces when power state control changes, and stream traces while mapping or checking DSP streams.

## State and Persistence
No driver state is stored here. Trace records snapshot register values, stream identifiers, channel maps, buffer positions, and status bits into trace buffers. These are diagnostic copies of transient hardware/driver state.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, Intel HDA SOF driver structures, and firmware IPC register definitions. Integrates with ALSA SOF Intel platforms, HDA interrupt handling, power management, IPC debugging, and PCM stream diagnostics.

## Risks
Hardware register semantics vary by platform and firmware generation. High-rate IRQ or stream-status tracing can be noisy. Consumers must interpret status bits with the matching Intel SOF platform documentation.

## Test Signals
Signals include Intel SOF boot, IPC ping/firmware response tracing, suspend/resume with D0I3C updates, PCM playback/capture IRQs, stream status transitions, and comparison against HDA register dumps.

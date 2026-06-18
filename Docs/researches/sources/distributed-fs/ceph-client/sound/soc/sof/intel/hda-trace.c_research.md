# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-trace.c

Purpose: provides DMA trace stream lifecycle support for SOF HDA platforms. It reserves a capture HDA stream, configures the trace DMA buffer, exposes its stream tag to firmware, triggers trace start/stop, and releases the stream.

Important APIs: `hda_dsp_trace_init()` obtains a DMI-L1-compatible capture stream and fills `sof_ipc_dma_trace_params_ext.stream_tag`; `hda_dsp_trace_prepare()` programs buffer size and calls `hda_dsp_stream_hw_params()`; `hda_dsp_trace_trigger()` delegates to `hda_dsp_stream_trigger()`; `hda_dsp_trace_release()` returns the stream.

Control flow: init allocates the stream first, then prepares BDL/registers. If prepare fails, it immediately puts the stream, clears `hda->dtrace_stream`, and resets stream_tag. Trigger assumes init succeeded and uses the stored stream. Release is idempotent only in the sense that it returns `-ENODEV` if no stream is open.

State and persistence: `sof_intel_hda_dev->dtrace_stream` is the only persistent runtime pointer. Buffer ownership belongs to the caller-supplied DMA buffer.

Dependencies and integration: relies on stream allocation/programming exports in `hda-stream.c` and is declared in `hda.h` for SOF trace ops.

Risks and test signals: risks include trigger-before-init null dereference, stream exhaustion, trace stream not released on higher-level error, and capture stream competition with PCM/probes. Test trace init/trigger/release, prepare failure cleanup, repeated trace sessions, and interaction with runtime PM/DMI L1.

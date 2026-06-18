# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-trace.c

Purpose: ACP firmware trace DMA stream setup and teardown.

Important APIs/types/functions: `acp_sof_trace_init()` reserves stream tag 8, assigns the trace DMA buffer, configures 16 pages, stores the stream in `adata->dtrace_stream`, and returns stream tag/physical offset in `sof_ipc_dma_trace_params_ext`. `acp_sof_trace_release()` releases that stream.

Control flow: init gets the fixed logger stream, configures PTEs with `acp_dsp_stream_config()`, and returns firmware parameters. On failure it releases the stream. Release looks up the saved stream and returns it to the pool.

State and persistence: `adata->dtrace_stream` persists while firmware trace is active. Stream tag 8 is reserved by convention for logging.

Dependencies and integration points: SOF core trace callbacks, ACP stream config, and firmware trace IPC parameters.

Risks: fixed tag 8 can conflict with other stream users if allocation discipline breaks. Release assumes `dtrace_stream` is valid; null-release behavior is not explicitly guarded.

Test signals: firmware trace enable/disable, trace DMA data flow, and stream resource release during remove/error paths.

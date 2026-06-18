# sources/distributed-fs/ceph-client/drivers/gpu/trace/Kconfig

Purpose: configuration switch for GPU memory usage tracepoints.

Important symbols: `TRACE_GPU_MEM` is a boolean option titled "Enable GPU memory usage tracepoints", defaulting to `n`.

Control flow: no runtime logic; the symbol controls whether the tracepoint provider object is built.

State and persistence: no state.

Dependencies and integration: intended for global and per-process GPU memory profiling and Android requirements. Its availability depends on GPU drivers emitting the trace events.

Risks: enabling the option exposes tracepoints but does not guarantee every driver reports useful data. The option is off by default, so tracing consumers must ensure kernel config support.

Test signals: build inclusion of `trace_gpu_mem.o` and runtime availability of `gpu_mem_total` tracepoint.

## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/trace.c

Purpose: materializes ath12k tracepoints by defining `CREATE_TRACE_POINTS` before including `trace.h`.

Important APIs/functions: it has no functions of its own; the tracepoint definitions from `trace.h` become actual tracepoint objects here.

Control flow: module compilation includes `<linux/module.h>`, sets `CREATE_TRACE_POINTS`, and includes the trace event header once.

State and persistence: no driver runtime state is owned here. Kernel tracing infrastructure owns enabled/disabled tracepoint state.

Dependencies/integration: depends on Linux tracepoint generation conventions and the local `trace.h` file. Other compilation units include `trace.h` without `CREATE_TRACE_POINTS` to call trace hooks.

Risks: duplicate `CREATE_TRACE_POINTS` inclusion elsewhere would cause link errors; missing this file would leave trace references unresolved in tracing builds.

Test signals: build with `CONFIG_ATH12K_TRACING` enabled and disabled; confirm tracepoint symbols and tracefs events exist when enabled.

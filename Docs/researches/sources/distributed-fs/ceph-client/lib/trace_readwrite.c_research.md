<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/trace_readwrite.c -->
# sources/distributed-fs/ceph-client/lib/trace_readwrite.c

## Purpose
Defines and exports MMIO read/write tracepoint helpers when `CONFIG_TRACE_MMIO_ACCESS` is enabled.

## APIs, Types, and Functions
With `CREATE_TRACE_POINTS`, includes `trace/events/rwmmio.h` to instantiate tracepoints. Under `CONFIG_TRACE_MMIO_ACCESS`, exports `log_write_mmio()`, `log_post_write_mmio()`, `log_read_mmio()`, and `log_post_read_mmio()`, plus tracepoint symbols `rwmmio_write`, `rwmmio_post_write`, `rwmmio_read`, and `rwmmio_post_read`.

## Control Flow, State, and Persistence
Each helper is a thin wrapper that forwards caller addresses, width, value where applicable, and `__iomem` address to the generated tracepoint. There is no local state or persistence.

## Dependencies and Integration
Depends on ftrace, module exports, `linux/io.h`, and the generated rwmmio trace events. It integrates with instrumented MMIO accessors or architecture code that calls these logging hooks.

## Risks and Test Signals
Risks include trace overhead on hot MMIO paths, incorrect caller-address plumbing by callers, and no compiled helpers when the config is off. Test signals include tracepoint visibility, correct pre/post event ordering, width/value/address encoding, and build coverage for both config states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/trace_readwrite.c -->

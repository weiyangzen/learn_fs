<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.c -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.c

Purpose: instantiates and exports MEI tracepoints for register and PCI config access.

Important APIs and functions: defines `CREATE_TRACE_POINTS`, includes `mei-trace.h`, and exports `mei_reg_read`, `mei_reg_write`, and `mei_pci_cfg_read` tracepoint symbols when not under sparse `__CHECKER__`.

Control flow: compile-time tracepoint generation only. Runtime users enable the tracepoints through ftrace/perf/tracefs; hardware code calls `trace_mei_*` helpers generated from `mei-trace.h`.

State and persistence: tracepoint enablement and ring-buffer data are managed by kernel tracing infrastructure. This file owns no driver state.

Dependencies and integration: depends on Linux module and tracepoint infrastructure and the local trace header. `hw-me.c`, `hw-txe.c`, and quirk/FW-status paths use the emitted tracepoints for observability.

Risks: tracepoint symbol names are ABI-like for in-kernel users; renaming them breaks out-of-tree instrumentation. The sparse guard avoids macro issues during static analysis but also means sparse does not instantiate tracepoint bodies here.

Test signals: build with tracing enabled, `tracefs` listing of `mei:mei_reg_read`, `mei:mei_reg_write`, and `mei:mei_pci_cfg_read`, and captured events during MEI probe/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.c -->

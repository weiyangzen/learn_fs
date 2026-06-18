<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.h

Purpose: declares MEI trace events for MMIO register reads, MMIO register writes, and PCI configuration reads.

Important APIs and types: `TRACE_SYSTEM mei` groups the events. `TRACE_EVENT(mei_reg_read)` records device name, register label, offset, and value. `TRACE_EVENT(mei_reg_write)` records analogous write data. `TRACE_EVENT(mei_pci_cfg_read)` records device name, register label, PCI config offset, value, and return code. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` direct trace generation to this local header.

Control flow: trace macros expand into static tracepoint call sites and metadata. Hardware code calls generated `trace_mei_reg_read()`, `trace_mei_reg_write()`, and `trace_mei_pci_cfg_read()` helpers; enabled tracepoints emit formatted events.

State and persistence: no driver state. Trace buffers are external kernel tracing state.

Dependencies and integration: includes Linux stringify/types/tracepoint/device headers. The header must be included once with `CREATE_TRACE_POINTS` from `mei-trace.c` and may be included by hardware code for call-site declarations.

Risks: format-string or field changes affect tooling that parses trace output. The final `#include <trace/define_trace.h>` must remain outside the include guard per tracing conventions.

Test signals: kernel build tracepoint generation, event presence under `/sys/kernel/tracing/events/mei/`, and register/PCI events while probing or resetting MEI hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/mei-trace.h -->

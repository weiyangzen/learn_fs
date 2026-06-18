# sources/distributed-fs/ceph-client/drivers/iommu/iommu-traces.c

## Purpose
This file instantiates and exports IOMMU tracepoints declared in `trace/events/iommu.h`. It has no runtime policy of its own; it exists so other core and driver code can emit standardized trace events for group membership, domain attachment, map/unmap, and page faults.

## Important APIs, Types, And Functions
`CREATE_TRACE_POINTS` before including `<trace/events/iommu.h>` materializes the tracepoint definitions.

Exported tracepoints are `add_device_to_group`, `remove_device_from_group`, `attach_device_to_domain`, `map`, `unmap`, and `io_page_fault`.

## Control Flow
There is no explicit function control flow beyond static tracepoint creation. Calls in `iommu.c` such as `trace_add_device_to_group()`, `trace_remove_device_from_group()`, `trace_attach_device_to_domain()`, `trace_map()`, `trace_unmap()`, and `trace_io_page_fault()` reach the generated tracepoint machinery when tracing is enabled.

## State And Persistence
The file contributes tracepoint registration metadata compiled into the kernel. Runtime state is managed by the tracing subsystem and trace buffers, not by this file. Trace output is transient unless userspace captures it.

## Dependencies And Integration Points
It depends on the kernel tracing infrastructure and `trace/events/iommu.h`. The exports let GPL modules hook or use these symbols. It integrates tightly with `iommu.c` map/unmap, group membership, domain attach, and fault paths.

## Risks
The risk surface is low, but tracepoint ABI names matter for observability tools. If tracepoint declarations and exports diverge, builds or module users fail. Since tracepoints may run on hot paths, their generated callbacks must remain efficient when disabled.

## Test Signals
Enable ftrace/perf trace events under the IOMMU event group, then exercise device probe, domain attach, IOVA map/unmap, and fault reporting. Expected events should appear without changing behavior when tracing is disabled.

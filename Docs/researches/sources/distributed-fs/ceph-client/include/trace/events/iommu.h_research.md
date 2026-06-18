# sources/distributed-fs/ceph-client/include/trace/events/iommu.h

Purpose: IOMMU tracing for group/device lifecycle, map/unmap operations, and IOMMU errors.

Important APIs/types/functions: Declares trace-event macros/classes `class:iommu_device_event`, `class:iommu_error`, `class:iommu_group_event`, `event:add_device_to_group`, `event:attach_device_to_domain`, `event:io_page_fault`, `event:remove_device_from_group`, `trace:map`, `trace:unmap`. Defines or exports symbolic enums/helpers none. Representative payload fields include `device`, `driver`, `flags:int`, `gid:int`, `iova:u64`, `paddr:u64`, `size:size_t`, `unmapped_size:size_t`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Group/device events record group ids and device names; map/unmap events record IOVA, physical address, size, and protection; error events capture reason and addresses. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: IOMMU domains and page tables persist outside tracing; trace entries hold transient translation metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Address traces can expose DMA layout, and protection/size mismatches can hide security-critical mapping bugs. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise device attach/detach, DMA map/unmap, and fault/error paths on an IOMMU-enabled system. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/iommu`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.

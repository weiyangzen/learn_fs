# sources/distributed-fs/ceph-client/include/trace/events/tlb.h

Purpose: Defines a single `tlb_flush` tracepoint with symbolic reasons for TLB invalidation activity.

Important APIs/types/functions: `TLB_FLUSH_REASON` registers enum values via `TRACE_DEFINE_ENUM` and provides symbolic output through `__print_symbolic`; `tlb_flush` records page count and reason.

Control flow: Architecture/MM TLB-flush paths call `trace_tlb_flush(reason, pages)`, which snapshots the reason code and page count into the trace buffer.

State/persistence: No TLB state is owned. It records flush events for profiling and debugging.

Dependencies/integration: Includes MM types and tracepoint infrastructure; consumed by MM/architecture code and performance tools.

Risks: Reason enums must stay synchronized with producers. Page-count interpretation may vary for full-ASID/full-mm flushes, so formatting must remain clear.

Test signals: Enable `tlb:tlb_flush` under mmap/munmap/page-fault workloads and compare emitted reasons with expected MM paths.

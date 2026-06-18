# sources/distributed-fs/ceph-client/include/trace/events/cma.h

## Purpose
`cma.h` traces Contiguous Memory Allocator release and allocation attempts, including retry on busy ranges.

## Important APIs, types, and functions
Events are `cma_release`, `cma_alloc_start`, `cma_alloc_finish`, and `cma_alloc_busy_retry`. They record area name, PFN, page pointer, counts, alignment, available/total counts, and error code.

## Control flow
CMA allocation emits start with requested and available/total pages, may emit busy retry events for contested ranges, and emits finish with final PFN/page/count/align/error. Release records the returned PFN/page/count.

## State and persistence behavior
No state is stored by the header. Records snapshot allocator state and selected pages for one allocation/release operation.

## Dependencies and integration points
It depends on basic Linux types, `struct page`, and tracepoints. It integrates with memory-management tracing and device-driver debugging for contiguous DMA allocations.

## Risks and test signals
Risks include high trace volume during allocation retry loops and pointer/PFN sensitivity. Test signals are CMA allocation success, allocation failure, busy retry under pinned pages, and release events with matching counts.

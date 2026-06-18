<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-heap.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-heap.h

## Purpose
Declares the DMA-BUF heaps allocation infrastructure, where named heaps allocate DMA-BUF objects for userspace or kernel consumers.

## Important APIs, Types, And Functions
Defines `struct dma_heap_ops` with mandatory `allocate()`, `struct dma_heap_export_info`, `dma_heap_get_drvdata()`, `dma_heap_get_name()`, `dma_heap_add()`, and global `mem_accounting`.

## Control Flow
A heap provider registers a named heap with private data and allocation ops. Consumers request allocations by heap name through the heap framework; the provider returns a `struct dma_buf` or an error pointer.

## State And Persistence
State is the registered heap object, provider private data, and allocations returned as DMA-BUFs. Heap registrations and buffers are runtime objects.

## Dependencies And Integration Points
Depends on DMA-BUF and heap provider drivers such as system, CMA, or vendor heaps. Integrates with userspace heap device nodes and memory accounting policy.

## Risks And Edge Cases
Heap names must be unique and stable. Allocation must validate length, fd flags, and heap flags. Providers must return proper error pointers and export DMA-BUFs with correct ops and reservation objects.

## Test Signals
Tests should cover heap registration, duplicate names, allocation success/failure, fd flags, heap private data lookup, name lookup, memory accounting toggles, and DMA-BUF lifetime after heap provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-heap.h -->

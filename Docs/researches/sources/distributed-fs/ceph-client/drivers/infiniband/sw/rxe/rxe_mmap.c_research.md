# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mmap.c

## Purpose
`rxe_mmap.c` implements RXE userspace mmap support for queue buffers created by CQ, QP, and SRQ verbs.

## Important APIs, types, and functions
Functions are `rxe_mmap_release()`, `rxe_mmap()`, and `rxe_create_mmap_info()`. VMA operations `rxe_vma_open()` and `rxe_vma_close()` maintain krefs. State is held in `struct rxe_mmap_info` declared in `rxe_loc.h`.

## Control flow
Queue creation calls `rxe_create_mmap_info()` to allocate metadata, assign a SHMLBA-aligned offset under `mmap_offset_lock`, record the ucontext and object buffer, and initialize a kref. Higher-level queue code adds it to `pending_mmaps` and returns the offset to userspace. `rxe_mmap()` searches the pending list for matching context and offset, rejects mappings larger than the object, removes the metadata from the pending list, remaps the vmalloc buffer with `remap_vmalloc_range()`, sets VMA ops/private data, and takes a mapping reference. VMA close drops the reference, and final release removes pending linkage, frees the vmalloc buffer, and frees metadata.

## State and persistence
Mmap metadata persists between object creation and userspace mmap, then for as long as VMAs reference the buffer. The queue buffer is freed from mmap release, so object cleanup and VMA refs must coordinate through krefs.

## Dependencies and integration points
It depends on RDMA ucontext/udata bundling, RXE pending mmap lists, vmalloc remapping, SHMLBA alignment, and queue allocation code in `rxe_queue.c`.

## Risks
Failed `remap_vmalloc_range()` after removing from the pending list leaves the metadata not pending but still referenced only by the creator unless caller cleanup handles it. Offset growth is monotonic and could wrap only over very long lifetimes, but there is no explicit overflow check. Context/offset matching is the main isolation check.

## Test signals
Test successful mmap for CQ/QP/SRQ queues, wrong context, wrong offset, too-large VMA, remap failure injection, fork/VMA open-close kref behavior, object destroy while mapped, and repeated create/mmap/destroy cycles.

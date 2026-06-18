# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ubuf.c

Purpose: converts user virtual-address ranges into an exported dma-buf that AMD XDNA can import as a GEM BO, enabling long-term pinned user memory submission.

Important APIs/functions: `amdxdna_get_ubuf()` copies a user VA table, validates page alignment and length overflow, enforces `RLIMIT_MEMLOCK` unless privileged, pins pages with `pin_user_pages_fast(FOLL_WRITE | FOLL_LONGTERM)`, exports a dma-buf with custom ops, and returns it for GEM prime import. dma-buf ops map pages to scatterlists, unmap/free sg-tables, release pins and pinned_vm accounting, mmap pages through PFN faults, and vmap/vunmap the pinned pages.

Control flow: `amdxdna_gem_create_ubuf_object()` calls this helper when a create-BO request supplies a VA table. The resulting dma-buf is immediately imported through AMD XDNA GEM prime import.

State and persistence: `amdxdna_ubuf_priv` stores pinned page array, page count, and grabbed mm. Pins and pinned_vm accounting persist until dma-buf release.

Dependencies: dma-buf framework, GUP/pagemap, scatterlist DMA mapping, VM fault insertion, resource limits/capabilities, and AMD XDNA UAPI VA entries.

Risks: long-term writable page pins can affect migration/COW and must be tightly accounted. Partial pin failure unwinds pinned pages by `start`. mmap faults assume pgoff is within pinned page count. Exported dma-buf size is accumulated from user entries.

Test signals: aligned/unaligned VA entries, overflow sizes, memlock limit enforcement, partial GUP failures, dma-buf map/unmap/vmap/mmap/release, and multiple VA entries with correct page ordering.

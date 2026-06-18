# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dmabuf.c

## Purpose

`uverbs_std_types_dmabuf.c` exports provider mmap pages as a dma-buf file descriptor through uverbs. It supports peer-to-peer dma-buf mapping, tracks revocation when the underlying mmap entry is removed, and waits for outstanding DMA mappings to unmap before final release.

## Important APIs, Types, and Functions

- `uverbs_dmabuf_ops` implements dma-buf attach, map, unmap, pin, unpin, and release.
- `UVERBS_METHOD_DMABUF_ALLOC` maps a userspace pgoff to a provider mmap entry, asks the provider for PFNs/phys vec, exports a dma-buf, links it into the mmap entry's dma-buf list, stores the dma-buf file in the uobject, and finalizes creation.
- `uverbs_dmabuf_fd_destroy_uobj()` revokes the dma-buf, invalidates mappings, waits for DMA reservation bookkeeping and kref completion, unlinks from the mmap entry, and drops the mmap-entry reference.
- `uverbs_dmabuf_map()` rejects mapping after revocation and creates an sg_table from the stored physical vector.

## Control Flow

Allocation reads `PGOFF`, resolves an `rdma_user_mmap_entry` through provider `pgoff_to_mmap_entry`, obtains PFNs via `mmap_get_pfns`, exports a dma-buf with `O_CLOEXEC`, initializes kref/completion/list state, and links the object under `mmap_entry->dmabufs_lock` unless the entry was already driver-removed. Destroy locks the mmap-entry list and dma-resv, marks revoked, deletes the list node, invalidates mappings, waits for reservation activity, drops the mapping kref, waits for completion, then releases the mmap entry.

## State and Persistence Behavior

State includes `ib_uverbs_dmabuf_file`, the exported `dma_buf`, dma-buf file stored as the uobject object, physical vector/provider pointer, `revoked` flag, kref/completion, and membership in `mmap_entry->dmabufs`. The object remains valid as an fd until release but mapping fails after revocation.

## Dependencies and Integration Points

The file depends on Linux dma-buf APIs, dma-resv, dma-buf physical-vector helpers, PCI P2P DMA, provider `pgoff_to_mmap_entry` and `mmap_get_pfns`, and `rdma_user_mmap_entry` lifetime rules. It imports the `DMA_BUF` namespace. MR registration can consume dma-buf FDs through `reg_user_mr_dmabuf`.

## Risks and Edge Cases

This file is concurrency-sensitive: revocation can race with dma-buf map/unmap, provider removal, fd release, and mmap-entry teardown. Correct kref/completion ordering prevents freeing memory while DMA mappings exist. Attach rejects non-peer2peer attachments. Pin is unsupported. Allocation failure after `dma_buf_export()` must drop both dma-buf and mmap-entry references.

## Test Signals

Test allocation from valid/invalid pgoff, driver removal between pgoff lookup and list insertion, peer2peer attach requirement, map after revoke returning `-ENODEV`, unmap kref completion, fd close before context initialization, dma-buf invalidation during provider removal, and MR registration using the exported fd.

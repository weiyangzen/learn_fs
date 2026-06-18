# sources/distributed-fs/ceph-client/drivers/infiniband/core/umem_dmabuf.c

## Purpose

`umem_dmabuf.c` implements RDMA UMEM objects backed by Linux DMA-BUF exporters instead of pages pinned directly from the caller's mm. It imports a DMA-BUF file descriptor, attaches it to an RDMA DMA device, maps the relevant subrange into an RDMA SG table, optionally pins the DMA-BUF, and supports revocation callbacks for exporters that can invalidate mappings.

## Important APIs, Types, and Functions

- `ib_umem_dmabuf_get` creates an unpinned DMA-BUF-backed UMEM using the RDMA device DMA device.
- `ib_umem_dmabuf_get_pinned`, `ib_umem_dmabuf_get_pinned_with_dma_device`, and `ib_umem_dmabuf_get_pinned_revocable_and_lock` create pinned variants. The revocable form returns with the reservation lock held so the driver can install a revoke callback.
- `ib_umem_dmabuf_map_pages` maps the DMA-BUF attachment, trims the SG table in place to match the requested offset and length, stores first/last trim metadata, and waits for exporter fences.
- `ib_umem_dmabuf_unmap_pages` restores the modified SG entries and unmaps the DMA-BUF attachment.
- `ib_umem_dmabuf_set_revoke_locked`, `ib_umem_dmabuf_revoke_lock`, `ib_umem_dmabuf_revoke_unlock`, `ib_umem_dmabuf_revoke`, and `ib_umem_dmabuf_release` manage revocation and release.

## Control Flow

Creation starts in `ib_umem_dmabuf_get_with_dma_device`. The function validates offset plus size overflow, obtains the `dma_buf` from the fd, checks that the requested end lies within `dmabuf->size`, allocates `struct ib_umem_dmabuf`, initializes the embedded `struct ib_umem`, rejects zero-page ranges, and dynamically attaches to the exporter with the selected attach ops. Pinned constructors then take the DMA reservation lock, call `dma_buf_pin`, mark `pinned`, map pages, and either return locked for revocable setup or unlock before returning.

Mapping requires the DMA reservation lock. If the UMEM was revoked, mapping fails. Otherwise it calls `dma_buf_map_attachment`, walks the DMA SG entries, counts entries overlapping the aligned requested range, trims the first entry start and last entry end in place, points the embedded UMEM SG table at the first relevant SG entry, and stores the mapped table. It then waits on the DMA reservation object so exporter migrations are complete before RDMA access proceeds. Unmapping restores the original first and last SG lengths/addresses before calling `dma_buf_unmap_attachment`.

Revocation is serialized by `dma_resv_lock`. `ib_umem_dmabuf_revoke_locked` invokes the driver's optional `pinned_revoke` callback, unmaps pages, unpins if needed, and marks the UMEM revoked exactly once. Release forces revocation, detaches from the exporter, drops the DMA-BUF reference, and frees the wrapper.

## State and Persistence

State is in `struct ib_umem_dmabuf`: embedded `ib_umem`, DMA-BUF attachment, mapped SG table, trim bookkeeping, pinned/revoked flags, optional callback and private pointer. There is no disk persistence. The object maintains external references to the DMA-BUF and attachment until release. The mapped SG table is deliberately modified while active and restored on unmap.

## Dependencies and Integration Points

The file depends on Linux DMA-BUF, DMA reservation/fence, DMA mapping, RDMA UMEM release dispatch, and driver memory-registration paths that accept DMA-BUF UMEMs. It imports the `DMA_BUF` namespace. The attach ops enable peer-to-peer support and optionally install `invalidate_mappings` for revocable pinned MRs.

## Risks

The highest risk is stale device DMA after an exporter revokes or migrates backing storage. Drivers using revocable pinned UMEMs must install the revoke callback before unlocking and must stop hardware access before the callback returns. SG list trimming is in-place, so failure to restore metadata can corrupt the exporter's SG table. Reservation locking is mandatory for map, unmap, revoke, and callback setup; missing it can race exporter invalidation. Waiting for fences may block indefinitely up to `MAX_SCHEDULE_TIMEOUT`, so timeout/error behavior needs coverage.

## Test Signals

Test signals include importing valid and too-small DMA-BUF fds, subrange offsets that trim first and last SG entries, mapping after revoke returning `-EINVAL`, release invoking the revoke path once, pinned and unpinned variants, custom DMA devices, exporter migration fences, and driver callbacks proving hardware access is quiesced before unmap. Lockdep should verify reservation-lock assertions in map/unmap/revoke paths.

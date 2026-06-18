# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/umr.c

## Purpose
`umr.c` implements mlx5 UMR (User-Mode Memory Registration) support used to update memory-key attributes and translation tables through a dedicated internal REG_UMR QP. It handles UMR resource initialization, synchronous WQE posting, QP recovery, MR revocation, PD/access reregistration, PAS/XLT updates for regular, ODP, dmabuf, and data-direct memory, and safe dmabuf page-size transitions.

## Important APIs, types, and functions
- `mlx5r_umr_init()`, `mlx5r_umr_cleanup()`, `mlx5r_umr_resource_init()`, and `mlx5r_umr_resource_cleanup()` allocate the internal PD and lazily create/destroy the UMR CQ/QP.
- `mlx5r_umr_qp_rst2rts()` transitions the REG_UMR QP through INIT, RTR, and RTS.
- `mlx5r_umr_post_send()`, `mlx5r_umr_post_send_wait()`, `mlx5r_umr_done()`, and `mlx5r_umr_recover()` post UMR WQEs, wait for completions, limit concurrency with a semaphore, and recover from QP error state.
- Mask helpers `get_umr_enable_mr_mask()`, `get_umr_disable_mr_mask()`, `get_umr_update_translation_mask()`, `get_umr_update_access_mask()`, `get_umr_update_pd_mask()`, and `umr_check_mkey_mask()` build and validate mkey update masks.
- `mlx5r_umr_revoke_mr()` fences DMA by moving an MR to a free/disabled state under the internal PD.
- `mlx5r_umr_rereg_pd_access()` updates MR PD and access flags.
- `mlx5r_umr_alloc_xlt()`, `mlx5r_umr_free_xlt()`, `mlx5r_umr_create_xlt()`, and `mlx5r_umr_unmap_free_xlt()` allocate, DMA-map, and free temporary translation buffers with an emergency page fallback.
- `_mlx5r_umr_update_mr_pas()`, `mlx5r_umr_update_mr_pas_range()`, `mlx5r_umr_update_mr_pas()`, `mlx5r_umr_update_data_direct_ksm_pas_range()`, and `mlx5r_umr_update_data_direct_ksm_pas()` update regular MTT or data-direct KSM PAS entries.
- `mlx5r_umr_update_xlt()` updates ODP translation entries, including optional indirect mkeys.
- `mlx5r_umr_update_mr_page_shift()`, `_mlx5r_umr_zap_mkey()`, and `mlx5r_umr_dmabuf_update_pgsz()` safely change dmabuf MR page size while avoiding partially exposed mappings.

## Control flow
Device initialization allocates an internal PD and initializes `umrc.init_lock`. The actual UMR CQ/QP is created lazily by `mlx5r_umr_resource_init()`, which uses acquire/release ordering to avoid repeated initialization, allocates a CQ, creates a REG_UMR QP, transitions it to RTS, initializes the concurrency semaphore, lock, and active state, and publishes the QP.

UMR updates build a `mlx5r_umr_wqe`, validate masks against hardware capabilities, acquire one semaphore slot, wait if recovery is active, post the WQE under `umrc.lock`, and wait for completion. Successful completions return directly. Flush completions are retried while the QP recovers. Other failures trigger recovery: mark recovery state, post a barrier WQE, wait for its flushed completion, reset the QP, transition it back to RTS, and mark active or error.

PAS update flows allocate a temporary XLT buffer sized as large as practical, fill MTT or KSM entries from `ib_umem` DMA blocks, sync the buffer for DMA, post one or more UMR WQEs with translation offsets, and free/unmap the buffer. ODP updates populate XLT entries through `mlx5_odp_populate_xlt()`. Dmabuf page-size updates first zap enough entries to make the mkey non-present, switch to a large safe page size, load remaining entries at the new page size, update the mkey page-size field, then reload the initially zapped entries.

## State and persistence
The internal `dev->umrc` state persists the PD, CQ, QP, semaphore, lock, initialization lock, and UMR state (`UNINIT`, active, recover, error). MR objects persist updated access flags, page shifts, and hardware mkey state after successful UMR commands. Temporary XLT buffers are freed after each update; `xlt_emergency_page` is a global fallback protected by `xlt_emergency_page_mutex`.

## Dependencies and integration points
This file integrates with mlx5 send-WQE construction helpers (`mlx5r_begin_wqe()`, `mlx5r_finish_wqe()`, doorbells), RDMA core PD/CQ/QP APIs, MR/mkey structures, ODP and dmabuf umem iteration, DMA mapping APIs, PCI relaxed ordering, mlx5 capability bits, data-direct KSM keys, and memory registration/reregistration code that calls these UMR helpers.

## Risks
- UMR QP recovery is concurrency-sensitive; incorrect state transitions can leave waiters spinning, leak semaphore slots, or post to an errored QP.
- The emergency XLT page serializes fallback allocations; any missing unlock in free paths can deadlock later UMR updates.
- Mask validation must match hardware capabilities for page-size, atomic, relaxed-ordering, and indirect-mkey updates.
- PAS chunking and translation offsets must be aligned to `MLX5_UMR_FLEX_ALIGNMENT`; misalignment can update wrong translation entries.
- Dmabuf page-size update intentionally avoids partially valid mappings. Reordering the zap/page-size/load steps can expose stale DMA mappings.
- Some error paths in ODP update return before unmapping/freeing XLT if not handled carefully; this area deserves leak-focused review when changed.
- `mlx5r_umr_revoke_mr()` treats internal device error as success because DMA is already stopped by catastrophic failure; tests should account for that semantic.

## Test signals
- Initialization tests should call UMR resource init concurrently and verify only one CQ/QP is created and later cleaned up.
- UMR post tests should cover successful WQEs, mask rejection, internal-error device state, semaphore concurrency, flushed completions, recovery success, and recovery failure.
- MR tests should cover revoke, PD/access reregistration, relaxed ordering, atomic access, zero-length MRs, and page-size update.
- PAS update tests should cover regular umem, dmabuf zap, data-direct KSM with relaxed-ordering key selection, partial range updates, and allocation fallback to smaller chunks/emergency page.
- ODP tests should cover direct and indirect XLT updates, invalid non-ODP calls, and unsupported indirect mkey capability.
- Dmabuf page-size tests should verify no stale mappings are exposed across the five-step update and that `mr->page_shift` is restored on failure.

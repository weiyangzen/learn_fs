# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/alloc.c

## Purpose

`alloc.c` provides mlx5 core memory allocation utilities for DMA-backed fragmented buffers and doorbell records. These helpers are used by queues and firmware object setup code that need page arrays, DMA addresses, and compact doorbell slots.

## Important APIs, Types, And Functions

- `struct mlx5_db_pgdir`: one DMA-coherent doorbell page, bitmap of free cache-line slots, and list node.
- `mlx5_frag_buf_alloc_node()` / `mlx5_frag_buf_free()`: allocate and free page-sized DMA coherent fragments for a logical buffer.
- `mlx5_db_alloc_node()` / `mlx5_db_free()`: allocate and free a doorbell record from a shared doorbell page.
- `mlx5_fill_page_frag_array_perm()` / `mlx5_fill_page_frag_array()`: fill firmware physical address arrays from fragment DMA mappings, optionally ORing low permission bits.
- `mlx5_dma_zalloc_coherent_node()`: temporarily sets the DMA device's NUMA node under `alloc_mutex` before `dma_alloc_coherent()`.

## Control Flow

Fragment buffer allocation computes `npages`, allocates a `mlx5_buf_list` array, then allocates each DMA-coherent fragment on the requested NUMA node. It validates DMA alignment against `page_shift`. Failure unwinds already allocated fragments and the array.

Doorbell allocation locks `dev->priv.pgdir_mutex`, scans existing page directories for a free bit, and if none exists allocates a new `mlx5_db_pgdir`. A free cache-line slot is cleared in the bitmap, `db->db` and `db->dma` are set to the slot, and the first two doorbell words are zeroed. Freeing sets the bit and destroys the entire page directory when all slots are free.

## State And Persistence Behavior

Runtime state is held in `dev->priv.pgdir_list`, each page directory's bitmap, and `struct mlx5_db` handles returned to callers. Fragment buffers hold their own `size`, `npages`, `page_shift`, and fragment list. No state persists across device teardown.

## Dependencies And Integration Points

The file depends on Linux DMA coherent allocation, NUMA node assignment, bitmaps, `cache_line_size()`, mlx5 DMA-device selection through `mlx5_core_dma_dev()`, and driver-private mutexes. Firmware-facing callers use the page arrays produced by `mlx5_fill_page_frag_array*()` in command inboxes.

## Risks

- `mlx5_dma_zalloc_coherent_node()` mutates the device node temporarily; the `alloc_mutex` must protect every such allocation path.
- Doorbell slots are cache-line-sized; wrong cacheline assumptions or double frees corrupt the bitmap/page lifetime.
- Fragment allocation frees failed fragments with `PAGE_SIZE`, while the last allocated fragment may be smaller only after success paths; alignment with the loop's `frag_sz` behavior should be preserved if changed.
- `WARN_ON(perm & 0xfc)` implies only low two permission bits are expected; callers passing other bits produce malformed physical address arrays.

## Test Signals

Exercise allocation/free across NUMA nodes, non-page-multiple sizes, injected DMA allocation failures at each fragment, doorbell page exhaustion and full-page release, double-free detection via debug configs, and firmware commands that consume `pas` arrays.

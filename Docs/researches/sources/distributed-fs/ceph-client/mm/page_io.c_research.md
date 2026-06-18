# sources/distributed-fs/ceph-client/mm/page_io.c

## Purpose
`page_io.c` implements swap activation block mapping plus swap writeout and swap read-in for folios. It bridges reclaim and fault paths to block devices, filesystem-backed swap operations, zswap, swap zero-page elision, cgroup I/O association, and VM accounting.

## Important APIs, Types, And Functions
- `generic_swapfile_activate()` maps a regular swapfile through `bmap()` into page-sized aligned swap extents.
- `swap_writeout()` is the high-level reclaim entry that handles stale swap cache, architecture swap preparation, zero-filled folio detection, zswap storage, memcg zswap writeback policy, and real swap I/O.
- `__swap_writepage()` selects filesystem swap, synchronous block device, or asynchronous block device write paths.
- `swap_read_folio()` handles swap-in accounting and selects zeromap, zswap, filesystem swap, synchronous block device, or asynchronous block device read paths.
- `struct swap_iocb` batches filesystem-backed swap I/O in `bio_vec` arrays and embeds a `kiocb`.
- `sio_pool_init()`, `swap_write_unplug()`, and `__swap_read_unplug()` manage the swap-I/O mempool and submit batched `mapping->a_ops->swap_rw()` requests.
- `end_swap_bio_write()`, `end_swap_bio_read()`, `sio_write_complete()`, and `sio_read_complete()` complete block or filesystem I/O.

## Control Flow
Swapfile activation scans file blocks in page-sized units, requires every page slot to map to contiguous PAGE_SIZE-aligned disk blocks, records extents, and updates `sis->max`, `sis->pages`, and span. Writeout first tries to free stale swap cache, lets architecture code preserve metadata, records zero-filled folios in `sis->zeromap` without I/O, clears stale zeromap bits for nonzero data, tries `zswap_store()`, checks memcg zswap writeback policy, and finally delegates to `__swap_writepage()`. Filesystem-backed writes accumulate contiguous pages in a `swap_iocb` until the plug is full or discontiguous, then submit through `swap_rw()`. Block-device writes build either a stack bio for synchronous I/O or an allocated bio for async completion. Read-in wraps submission time in workingset delayacct/PSI accounting, services zeromap by zeroing and marking uptodate, tries `zswap_load()`, protects zswap if backing I/O is required, and submits via the selected filesystem or block path.

## State And Persistence Behavior
Persistent external state is the swap area contents and swap extent mapping stored in `swap_info_struct`. Runtime state includes folio dirty/writeback/uptodate/lock/reclaim bits, swapcache membership, `sis->zeromap`, zswap entries, memcg and objcg counters, VM events, `swap_iocb` objects from `sio_pool`, and bio ownership. Failed writes redirty pages and clear reclaim; successful reads mark folios uptodate and unlock them.

## Dependencies And Integration Points
This file integrates with reclaim, swap cache, block layer bios, filesystem `swap_rw`, `bmap`, zswap, memcg, blkcg, objcg accounting, PSI and delay accounting, THP/mTHP stats, architecture swap hooks, task lifetime handling for synchronous swap reads, and swap extent management from `mm/swapfile.c`.

## Risks
- Swapfile activation rejects holes, discontiguity, and misalignment; filesystem changes to `bmap()` behavior can make swap activation unsafe or unavailable.
- Zeromap correctness depends on clearing old bits before nonzero writes and handling large folios only when the queried zeromap batch is complete.
- Filesystem swap batching must not merge requests across files or noncontiguous offsets.
- Completion paths must always end writeback or unlock folios exactly once, even on partial filesystem I/O.
- Data-race reads of immutable swap flags rely on those flags not changing for the selected I/O mode.

## Test Signals
- Swapon regular files with holes, discontiguous blocks, and aligned extents.
- Swap out/in zero-filled and nonzero small and large folios, verifying `SWPOUT_ZERO`/`SWPIN_ZERO` and absence of stale zero reads.
- Exercise zswap hit, miss, store, writeback-disabled, and backing-device fallback paths.
- Test filesystem-backed swap with plugged contiguous I/O and discontiguous unplug boundaries.
- Inject block and filesystem I/O errors and verify dirtying, unlock/writeback completion, and ratelimited alerts.

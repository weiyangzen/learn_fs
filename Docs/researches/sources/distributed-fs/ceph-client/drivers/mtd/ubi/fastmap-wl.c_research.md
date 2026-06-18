# sources/distributed-fs/ceph-client/drivers/mtd/ubi/fastmap-wl.c

## Purpose
`fastmap-wl.c` extends wear-leveling behavior for fastmap. It manages fastmap anchor PEB selection, user and WL fastmap pools, synchronous pool refill, asynchronous fastmap update work, and returning fastmap-owned PEBs to WL erase scheduling.

## Important APIs, Types, And Functions
Key functions are `ubi_wl_get_fm_peb()`, `ubi_refill_pools_and_lock()`, `ubi_wl_get_peb()`, `ubi_ensure_anchor_pebs()`, `ubi_wl_put_fm_peb()`, `ubi_is_erase_work()`, `ubi_fastmap_close()`, and `may_reserve_for_fm()`. Helpers include `update_fastmap_work_fn()`, `find_anchor_wl_entry()`, `return_unused_pool_pebs()`, `wait_free_pebs_for_pool()`, `left_free_count()`, `can_fill_pools()`, `produce_free_peb()`, `next_peb_for_wl()`, `need_wear_leveling()`, and `get_peb_for_wl()`.

## Control Flow
Fastmap needs an anchor PEB below `UBI_FM_MAX_START`. `ubi_wl_get_fm_peb()` removes either an anchor candidate or mean WL entry from the free RB-tree under `wl_lock`. `ubi_refill_pools_and_lock()` first waits for enough free PEBs, then takes `fm_protect`, `work_sem`, and `fm_eba_sem` in write mode, returns unused pool PEBs to the free tree, returns an existing anchor, chooses a new anchor, and fills the user and WL pools from free WL entries.

`ubi_wl_get_peb()` is the EBA-facing allocator. It takes `fm_eba_sem` in read mode, updates fastmap when pools are exhausted, returns a PEB from `fm_pool`, protects it in WL state, and intentionally returns with the read semaphore held so EBA can safely update mappings before `up_read()`. WL-internal allocation uses `fm_wl_pool`; when empty in atomic contexts it schedules `fm_work` instead of updating fastmap synchronously.

`ubi_ensure_anchor_pebs()` tries to reserve an anchor immediately or schedules wear leveling to produce one. `ubi_wl_put_fm_peb()` maps fastmap superblock/data PEBs to internal fastmap volume IDs and schedules erase, handling the first attach case where WL has not seen the PEB before.

## State And Persistence
State includes `ubi->fm_pool`, `ubi->fm_wl_pool`, `ubi->fm_anchor`, `fm_work_scheduled`, `fm_pool_rsv_cnt`, free/used/protected WL trees, and work queues. Persistent state is affected when pool exhaustion or volume changes cause `ubi_update_fastmap()` to write a new on-flash fastmap. Unused pool PEBs are not free until explicitly returned to WL.

## Dependencies And Integration Points
The file is tightly coupled to WL internals (`wl_tree_add`, `wl_get_wle`, `find_wl_entry`, `schedule_erase`, `do_work`, `wear_leveling_worker`, `erase_worker`), EBA via `fm_eba_sem`, and fastmap writing via `ubi_update_fastmap()`. It is included in the UBI WL build rather than standing alone with its own includes.

## Risks
Semaphore ownership is subtle: callers of `ubi_wl_get_peb()` must release `fm_eba_sem`, and error paths also return with the semaphore held in some cases. Pool accounting must not consume PEBs needed for WL/EBA/bad-block reserves or fastmap blocks themselves. Anchor scarcity can force wear leveling or fastmap update failure. Asynchronous `fm_work_scheduled` prevents repeated scheduling, so missed clearing could stall updates.

## Test Signals
Test pool refill with low free counts, anchor selection below `UBI_FM_MAX_START`, pool exhaustion triggering fastmap update, async WL pool refill scheduling from atomic contexts, return of unused pool PEBs during close/update, bad first-fastmap recovery where `lookuptbl[pnum]` is missing, and semaphore balance around EBA writes.

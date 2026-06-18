# sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.c

Purpose: this file implements UBI wear leveling, scrubbing, physical eraseblock lifecycle, asynchronous erase work, bad-block handling, and the UBI background thread. It operates on PEBs and erase counters, while EBA maps logical data onto the PEBs it provides.

Important APIs, types, and functions: main entry points are `ubi_wl_init()`, `ubi_wl_close()`, `ubi_wl_get_peb()`, `ubi_wl_put_peb()`, `ubi_wl_scrub_peb()`, `ubi_wl_flush()`, `ubi_sync_erase()`, `ubi_bitflip_check()`, and `ubi_thread()`. Core helpers include `wl_tree_add()`, `wl_get_wle()`, `find_wl_entry()`, `find_mean_wl_entry()`, `prot_queue_add()`, `prot_queue_del()`, `schedule_erase()`, `wear_leveling_worker()`, `ensure_wear_leveling()`, `__erase_worker()`, `serve_prot_queue()`, `do_work()`, `shutdown_work()`, and `erase_aeb()`.

Control flow: initialization builds WL entries from attach lists: free PEBs enter the free RB-tree, used PEBs enter used or scrub trees, erase-list PEBs get scheduled, and fastmap PEBs are linked or erased. `ubi_wl_get_peb()` chooses a mean erase-counter free PEB, removes it from free, places it in the protection queue, verifies its writable area is all-FF, and returns the PEB number. `ubi_wl_put_peb()` removes a PEB from used/scrub/erroneous/protection state or coordinates with an active move, then schedules erase work. The background thread drains work items. Erase work calls `ubi_sync_erase()`, writes a new EC header, returns the PEB to free or fastmap anchor state, advances the protection queue, and schedules WL if needed.

State and persistence behavior: runtime state lives in `ubi_device`: used/free/scrub/erroneous RB-trees, protection queue, lookup table, pending work list, move markers, max EC, bad PEB accounting, reserve accounting, and background-thread state. Persistent state changes are EC increments and EC header writes, PEB erasures, bad-block marks, and copied VID/data from wear-leveling moves. The protection queue delays moves for newly allocated PEBs by a number of erase cycles.

Dependencies and integration points: WL calls IO for erase/header writes/bitflip checks, EBA for copying LEBs during moves, fastmap hooks when enabled, misc reserve helpers for bad-block accounting, and Linux kthreads/freezer/rbtree/locking infrastructure. EBA calls WL to get/put/scrub PEBs and flush pending erases for volume operations.

Risks: the move state machine is concurrency-sensitive: `move_from`, `move_to`, `move_to_put`, `move_mutex`, `wl_lock`, `work_sem`, `fm_eba_sem`, and `fm_protect` must remain correctly ordered. Error classification determines whether to protect, scrub, torture, mark erroneous, erase, or switch the whole device read-only. `ubi_wl_get_peb()` returns with `fm_eba_sem` held in the non-fastmap path according to its comment, so call pairing must be audited with EBA. Bad-block reserve exhaustion can force read-only mode. Fastmap anchor reservation alters free-tree selection.

Test signals: attach initialization should account for every good PEB exactly once; free/used/scrub/erroneous/protection transitions should satisfy debug self-checks; wear leveling should trigger when EC difference exceeds threshold; bitflips should schedule scrubbing and return `-EUCLEAN`; erase failures should mark bad PEBs and update reserves; background-thread failure count should switch to read-only after repeated errors; `ubi_wl_flush()` should drain targeted work; and fastmap-enabled builds should preserve anchors and pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.c -->

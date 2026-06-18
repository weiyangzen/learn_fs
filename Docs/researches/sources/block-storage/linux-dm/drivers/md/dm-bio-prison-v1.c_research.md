# File Research: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v1.c

Implements the original Device Mapper "bio prison": a spinlock-protected red-black tree of keyed cells used to detain bios that cannot be processed immediately. Keys compare by virtual/physical namespace, thin device id, and overlapping block ranges; overlapping keys resolve to the same cell, so only one holder proceeds while later bios are appended to that cell.

The prison owns a mempool backed by `dm_bio_prison_cell` slab objects with a minimum of 1024 cells. Public entry points allocate/free cells, create/destroy prisons, get or create cells, detain bios, release cells, release without holder, error all bios, visit-and-release under lock, and promote a waiting inmate to holder.

Release paths erase the cell from the rb-tree and optionally merge the holder and inmates into a caller-provided `bio_list`. Error release sets `bi_status` and completes each bio. Promotion avoids a race between empty-cell release and new inmates by deciding under the prison lock.

The second half implements `dm_deferred_set`, a 64-entry ring of deferred counters and work lists used to delay work until earlier shared reads complete. `dm_deferred_entry_inc()` pins the current entry; `dm_deferred_entry_dec()` decrements and sweeps ready work; `dm_deferred_set_add_work()` either queues work behind outstanding entries or returns that no deferral is needed. Module init/exit initializes both v1 and v2 bio-prison slab caches.

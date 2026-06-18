# sources/distributed-fs/ceph-client/drivers/md/bcache/request.h

Purpose: declares the request-layer insertion operation, public submit hooks, congestion helper, and request slab symbol.

Important APIs/types: `struct data_insert_op` embeds a closure, cache set, bio, target workqueue, inode, write point, priority, status, flags, keylist, and padded replace key. Flags distinguish bypass, writeback, flush-journal, checksum, replace, replace collision, and insertion completion. `CLOSURE_CALLBACK(bch_data_insert)` is the shared cache insertion entry point. `cached_dev_submit_bio()` and `flash_dev_submit_bio()` are installed as block make-request style handlers through init functions. `bch_get_congested()` is used by bypass policy. `bch_search_cache` is the slab for `struct search` from `request.c`.

Control flow: callers initialize `data_insert_op` fields, set `bio`, `inode`, `c`, and workqueue, then call `bch_data_insert()` as a closure. Cached and flash device init functions install the appropriate cache-miss and ioctl hooks into device structs.

State and persistence: this header defines the state container that eventually writes cache data and B-tree keys. The `replace_key` member is the persistence guard for read-miss fills and moving GC replacements.

Dependencies/integration: relies on closure callbacks, Linux `bio`, `blk_status_t`, `struct keylist`, and B-tree key layout macros. It is included by moving GC and other request users.

Risks/test signals: bitfield layout is packed through a `union` with `uint16_t flags`; any new flags must fit and preserve initializer expectations. Tests should cover initialization of all public request hooks, data insertion with replace and non-replace modes, and flag combinations such as bypass plus flush journal or checksum plus writeback.

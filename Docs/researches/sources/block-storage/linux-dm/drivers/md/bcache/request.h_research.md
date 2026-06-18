# File Research: sources/block-storage/linux-dm/drivers/md/bcache/request.h

`request.h` exposes the request-layer API and defines `struct data_insert_op`, the closure state used by cache insertion, writeback, flash-volume writes, and moving GC. The structure carries the cache set, bio, workqueue, inode/device id, write point/priority, block status, flags, generated insert keylist, and optional replacement key.

The flag union names the insertion modes: bypass invalidation, writeback/dirty insertion, journal flushing, checksum generation, replacement insertion, replacement collision reporting, and insert completion. This common structure is the bridge between request handling, moving GC, and writeback.

The header declares congestion probing, data insertion, cached-device and flash-device request initialization, block-layer submit functions, and the `bch_search_cache` slab. It assumes the broader bcache type definitions from `bcache.h`.

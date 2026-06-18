## sources/distributed-fs/ceph-client/fs/iomap/internal.h

Purpose: private header shared by iomap implementation files. It defines internal batching and helper declarations that are not part of the public `linux/iomap.h` API.

Important APIs/types: `IOEND_BATCH_SIZE` limits buffered/direct ioend completion batching. `iomap_max_bio_size` returns `BIO_MAX_SIZE` normally, but for `IOMAP_F_INTEGRITY` uses `max_integrity_io_size(bdev_limits(iomap->bdev))` so integrity metadata allocations remain bounded. It declares `iomap_finish_ioend_buffered_read`, `iomap_finish_ioend_direct`, and `iomap_bio_read_folio_range_sync`; the latter has a `CONFIG_BLOCK` stub returning `-EIO`.

Control flow and state: this header has no runtime control flow or persistent state, but its inline helper shapes bio sizing in both direct and buffered writeback paths.

Dependencies and integration points: depends on block-layer bio limits, integrity support, and the internal `struct iomap_ioend` used across iomap read/write completion files. The `CONFIG_BLOCK` guard lets non-block builds compile callers with a clear failure path.

Risks and test signals: bio size mistakes can cause integrity-buffer over-allocation or excessive latency. Test signals are integrity-enabled writeback/direct-I/O workloads, very large bios, and non-`CONFIG_BLOCK` compile coverage.

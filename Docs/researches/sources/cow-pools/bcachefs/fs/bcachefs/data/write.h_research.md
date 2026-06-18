# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/write.h

Public write-path API and small helpers.

Key contents:
- Includes checksum and write type definitions.
- Defines `to_wbio()` container helper.
- Declares bounce-page pool helpers, replica bio submission, write error logging, overwrite accounting, and extent update.
- Provides `index_update_wq()` to route copygc writes to `copygc.wq` and other writes to `btree_update_wq`.
- Defines `bch2_write_op_init()` initializer for `struct bch_write_op`.
- Declares `bch2_write`, `bch2_write_point_do_index_updates()`, write flag string table, write-op text helpers, and fs write init/exit.
- Provides `wbio_init()` to clear the embedded write-bio state while preserving the containing bio.

Important invariants:
- `bch2_write_op_init()` establishes safe defaults: no flags, no error, default checksum/compression from inode opts, normal watermark, empty device/open bucket lists, `POS_MAX`, and no disk reservation.
- `index_update_wq()` keeps copygc index work on its own queue.

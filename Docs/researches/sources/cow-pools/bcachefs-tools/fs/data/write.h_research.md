# File Research: sources/cow-pools/bcachefs-tools/fs/data/write.h

## Role

Public declarations and small helpers for the write path.

## Key Exports

- `to_wbio()` maps an embedded `struct bio` to `struct bch_write_bio`.
- Bounce-page pool helpers: `bch2_bio_free_pages_pool()` and `bch2_bio_alloc_pages_pool()`.
- Replica submission: `bch2_submit_wbio_replicas()`.
- Error logging: `bch2_write_op_error()`.
- Extent accounting/update helpers: `bch2_sum_sector_overwrites()` and `bch2_extent_update()`.
- Write closure entry point: `bch2_write`.
- Write-point index update worker: `bch2_write_point_do_index_updates()`.
- Formatting and filesystem init/exit helpers.

## `bch2_write_op_init()`

Initializes a `bch_write_op` with filesystem pointer, zeroed state, checksum/compression defaults from inode options, normal watermark, empty open-bucket and device lists, max position defaults, zero version, empty disk reservation, unlimited new file size, and no flush-device mask.

## Workqueue Selection

`index_update_wq()` routes copygc-watermark writes to `c->copygc.wq`; all other index updates use `c->btree_update_wq`.

## Bio Initialization

`wbio_init()` zeroes the write-bio private prefix while preserving the embedded bio object.

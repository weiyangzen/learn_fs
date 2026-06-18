# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/read.h

## Role

`read.h` declares the read path API and defines `struct bch_read_bio`.

## Main Types

`struct bch_read_bio` extends `struct bio` with:
- filesystem/device references,
- timing fields,
- parent/end_io union for split reads,
- saved iterator,
- read flags and state bits,
- decoded chosen pointer,
- read/data positions,
- bversion,
- inode I/O options,
- failure and error-report pointers,
- work item.

`struct bch_read_err_report` accumulates read error bits and formatted messages under a mutex.

## Helpers

- `bch2_read_indirect_extent()`: resolves `KEY_TYPE_reflink_p` into `BTREE_ID_reflink` data.
- `bch2_read_extent()`: inline wrapper around `__bch2_read_extent()` for one extent.
- `rbio_init_fragment()` and `rbio_init()`: initialize split/parent read bios.
- `to_rbio()`: gets `bch_read_bio` from a bio.

## Constants

- `BIO_BOUNCE_BUF_POOL_LEN`
- read error bits for checksum, I/O, decompression, and EC reconstruction

## Exported Functions

- `bch2_read()`
- `__bch2_read_extent()`
- `bch2_read_err_msg_trans()`
- `bch2_promote_op_to_text()`
- `bch2_read_bio_to_text()`
- `bch2_fs_io_read_init()` / `bch2_fs_io_read_exit()`

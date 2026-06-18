# File Research: sources/cow-pools/bcachefs-tools/fs/data/read.h

## Purpose
Public structures and entry points for the bcachefs data read path.

## Main Interfaces and Behavior
- Defines bounce buffer pool length and read error bitmasks for checksum, IO, decompression, and EC reconstruction.
- `struct bch_read_err_report` aggregates errors and messages under a mutex.
- `struct bch_read_bio` extends `struct bio` with filesystem/device refs, timing, parent/endio union, saved iterator, extent offsets, flags/state bits, selected decoded pointer, read/data positions, inode opts, failure/report pointers, and work item.
- State bits distinguish data update reads, verify-decompress, promotion, bounce, split, CRC narrowing, observed errors, self-heal, and workqueue context.
- `bch2_read_indirect_extent()` resolves `KEY_TYPE_reflink_p` through `bch2_lookup_indirect_extent()`, switches data btree to reflink, and reassembles the target extent.
- Declares error message rendering, `__bch2_read_extent()`, inline `bch2_read_extent()`, top-level `bch2_read()`, rbio fragment/original initializers, promotion/read text renderers, and fs read init/exit.

## Risks and Invariants
- Split rbios store `parent`; unsplit rbios store original `end_io` in the same union.
- `rbio_init_fragment()` inherits opts and error reporting from the original rbio.

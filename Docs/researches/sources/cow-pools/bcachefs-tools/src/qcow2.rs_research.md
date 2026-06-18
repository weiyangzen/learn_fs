# File Research: sources/cow-pools/bcachefs-tools/src/qcow2.rs

Implements a minimal QCOW2 v2 sparse image writer and reader, used by dump/undump style workflows.

Range helpers:
- `range_add`, `ranges_roundup`, `ranges_sort_merge`, and `ranges_sort` maintain sparse byte ranges.
- Ranges are rounded to block boundaries and merged before writing.

I/O helpers:
- `pread_exact` and `pwrite_all` loop until complete and retry `EINTR`.
- `file_size_fd` handles regular files and block devices using `BLKGETSIZE64`.

Writer:
- `Qcow2Image::new` calculates L1/L2 table sizes from input size and QCOW block size.
- `write_buf` writes raw data at the current output offset and maps each source block through L2 entries.
- `flush_l2` writes pending L2 tables and records them in L1 with `QCOW_OFLAG_COPIED`.
- `write_ranges` reads selected source ranges block by block and writes only those blocks.
- `finish` flushes L2, writes L1, then writes the big-endian QCOW2 header.

Reader:
- `qcow2_to_raw` validates magic/version, truncates output to image size, reads L1/L2 tables, and writes mapped blocks back to raw positions.
- Sparse/unmapped blocks remain holes or zeros depending on output filesystem behavior.

Limitations:
- Supports QCOW2 version 2 only.
- Does not implement refcount tables, snapshots, backing files, compression, encryption, or extended headers.
- The header sets refcount metadata to zero, making this a specialized internal sparse container rather than a general-purpose QCOW2 implementation.

Potential concerns:
- `Qcow2Image::new` asserts block size is a power of two rather than returning an error.
- `finish` advances `offset` by rounded L1 size but writes only unpadded L1 bytes; this is fine as final metadata but leaves unwritten padding implicit.

# sources/distributed-fs/ceph-client/fs/btrfs/zlib.c

## Purpose

`zlib.c` implements the Btrfs zlib compression backend. It allocates zlib workspaces, compresses filemap folios into compressed bios, decompresses compressed bios into target pages, and supports single-sector inline decompression. It also contains a special input-buffer path for s390 zlib hardware acceleration.

## Important APIs, Types, And Functions

`struct workspace` wraps `z_stream`, a scratch buffer, buffer size, list node, and compression level. `zlib_get_workspace()` retrieves a generic Btrfs compression workspace and records the requested level. `zlib_alloc_workspace()` allocates the zlib workspace memory, scratch buffer, and stream workspace. `zlib_free_workspace()` releases all allocations.

`need_special_buffer()` detects s390 DFLTCC hardware acceleration and requests a 4-page buffer when the filesystem folio size is too small. `copy_data_into_buffer()` gathers input filemap data into that buffer so hardware compression receives a larger contiguous input span.

`zlib_compress_bio()` initializes deflate, streams input folios from the file mapping, fills compressed output folios, and appends them to `cb->bbio.bio`. It aborts with `-E2BIG` if compression expands data past useful thresholds or bio append fails, with `-ENOMEM` on allocation failure, and with `-EIO` on zlib failures.

`zlib_decompress_bio()` maps compressed bio folios, optionally skips the zlib header and adler32 path for raw deflate when safe, inflates into the workspace buffer, and feeds output to `btrfs_decompress_buf2page()`. `zlib_decompress()` handles the smaller direct decompression path into a destination folio and zero-fills any short output. `btrfs_zlib_compress` declares supported levels 1 through 9 and the default.

## Control Flow And Integration

Compression starts from the generic Btrfs compression framework with a `compressed_bio`. The backend initializes zlib, obtains input from the inode mapping via `btrfs_compress_filemap_get_folio()`, maps folios with `kmap_local_folio()`, and pushes full or partial compressed folios into the bio. Once all input is consumed it repeatedly calls deflate with `Z_FINISH` until `Z_STREAM_END`.

Bio decompression iterates compressed bio folios using `folio_iter`, inflates into a sector-sized or special workspace buffer, and copies decompressed ranges into the original compressed-bio destination pages. The direct decompression path assumes both compressed input and decompressed output fit within one sector-sized workspace.

## State And Persistence Behavior

The file has no on-disk metadata logic of its own. Its persistent effect is the compressed byte stream stored by higher Btrfs writeback code. Workspace objects are reusable runtime state and keep no cross-call compression history after `zlib_deflateEnd()` or `zlib_inflateEnd()`. Error returns tell the compression framework whether to store data uncompressed (`-E2BIG`) or fail IO (`-EIO`, `-ENOMEM`).

## Dependencies

It depends on Linux zlib/zutil, bio, folio/page mapping, slab/vmalloc allocation, and Btrfs compression helpers (`compression.h`, `btrfs_inode.h`, `fs.h`, `subpage.h`). The implementation relies on `btrfs_min_folio_size()`, `btrfs_alloc_compr_folio()`, `btrfs_free_compr_folio()`, `btrfs_calc_input_length()`, and `btrfs_decompress_buf2page()`.

## Risks And Edge Cases

The main risks are folio lifetime and local mapping balance, output-size accounting, and correctly freeing the last unused output folio. The s390 special buffer path copies across potentially multiple folios and must advance `start` and `avail_in` accurately. Header-skipping logic must only use raw inflate when the input is recognizable deflate without preset dictionary. Short decompression must zero-fill to avoid exposing stale data. Compression expansion detection must be conservative enough to avoid writing compressed extents larger than the original.

## Test Signals

Useful signals include mount/write/read tests with `compress=zlib` at levels 1, default, and 9; incompressible data fallback; compressed reads across multiple folios and subpage sectors; inline/direct decompression; fault injection for workspace and output folio allocation; corrupt compressed extent read errors; fstests compression coverage; and architecture coverage for DFLTCC-enabled s390 systems.

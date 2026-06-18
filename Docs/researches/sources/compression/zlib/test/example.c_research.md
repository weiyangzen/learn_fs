# sources/compression/zlib/test/example.c

`example.c` is zlib's canonical executable smoke test and usage sample. It demonstrates one-shot `compress()`/`uncompress()`, gzip file I/O through `gz*`, streaming `deflate()`/`inflate()`, full-flush recovery with `inflateSync()`, dynamic `deflateParams()` changes, and preset dictionary negotiation.

Important APIs include `Byte`, `uLong`, `z_stream`, allocator callbacks, `gzFile`, zlib return codes, flush modes, and version helpers. `test_compress()` validates helper compression. `test_gzio()` covers `gzopen`, `gzputc`, `gzputs`, `gzprintf`, `gzseek`, `gzread`, `gzgetc`, `gzungetc`, `gzgets`, `gztell`, and `gzclose`. Stream tests force tiny buffers, large buffers, full flush, sync recovery, and dictionary handling.

`main()` checks linked/header version compatibility, allocates zeroed buffers, runs the tests in a fixed order, then frees memory. State is mostly in `z_stream` internals and caller buffers; `dictId` persists the Adler-32 dictionary identifier. The gzip test can create a platform-specific `foo.gz` style file. Integration points are the public zlib ABI and CMake package tests that compile this file against shared/static imported targets.

Risks include first-failure exit hiding later failures, current-directory file writes, assumptions around buffer casts to `uInt`, and conditional coverage gaps under `Z_SOLO` or `NO_GZCOMPRESS`. Test signals are stdout success lines plus nonzero exit and stderr diagnostics on any API mismatch.

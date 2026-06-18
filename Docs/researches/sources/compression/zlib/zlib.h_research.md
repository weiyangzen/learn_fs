# sources/compression/zlib/zlib.h

`zlib.h` is zlib's primary public API and license header. It declares stream compression/decompression, gzip file I/O, utility compression helpers, checksums, versioning, compile flags, large-file variants, initialization macros, and selected undocumented compatibility exports.

Core types are `alloc_func`, `free_func`, `z_stream`, `z_streamp`, `gz_header`, `gz_headerp`, `gzFile`, `in_func`, and `out_func`. Constants cover flush modes, return codes, compression levels, strategies, data type guesses, `Z_DEFLATED`, and `Z_NULL`. Major APIs include `deflate*`, `inflate*`, `inflateBack*`, `compress*`, `uncompress*`, `gz*`, `adler32*`, `crc32*`, and `zlibCompileFlags()`.

Control flow is encoded as API lifecycle contracts: initialize streams with macros that pass `ZLIB_VERSION` and `sizeof(z_stream)`, repeatedly provide buffers and call `deflate()`/`inflate()`, then reset/copy/end. Gzip flow opens, optionally configures buffers/params, performs I/O/seek/flush, and closes. State is split between caller-visible `z_stream` fields and hidden `internal_state`; `gzFile` is semi-opaque with a small exposed struct for the fast `gzgetc` macro.

Dependencies include `zconf.h`, C++ linkage, RFC 1950/1951/1952 formats, and all implementation files. Risks are public ABI instability, comment/API mismatch, subtle nonfatal errors such as `Z_BUF_ERROR`, deferred gzip errors, macro remapping surprises, and the intentionally unchecked `gzgetc` macro. Test signals are downstream compilation, runtime stream/gzip/checksum tests, large-file alias tests, and ABI version mismatch checks.

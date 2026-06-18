# sources/compression/zlib/contrib/iostream2/zstream.h

Purpose: provides a compact C++ wrapper for gzip binary and formatted output using zlib `gz*` APIs.

Important APIs/types/functions: `izstream`, `ozstream`, helper `zstringlen`, template `read()`/`write()`, operators `>` for binary input and `<` for binary output/string records, and `operator<<` forwarding formatted output to an internal `ostrstream`.

Control flow: `izstream` opens or attaches gzip input, reads raw objects with `gzread`, decodes strings by reading a one-byte or full-word length prefix, and closes with `gzclose`. `ozstream` opens or attaches gzip output with a compression level in the mode string, writes raw objects with `gzwrite`, buffers formatted output in `ostrstream`, flushes that buffer before binary writes or explicit flush/close, and closes the file.

State and persistence: each stream owns a `gzFile`; `ozstream` also owns a lazily allocated `ostrstream` used for text formatting. Gzip files persist at supplied paths or descriptors.

Dependencies/integration: depends on old `<strstream.h>`, `<iomanip.h>` style users, zlib, and platform binary mode setup for Windows.

Risks: binary serialization is not portable across endianness or type sizes. `close()` calls `gzclose(m_fp)` even when `m_fp` may be null. The string length encoding uses `size_t`, so archives are ABI-dependent. `ostrstream::str()` ownership is manually deleted.

Test signals: `zstream_test.cpp` writes and reads three strings, then writes formatted text to `temp.gz`.

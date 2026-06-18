# sources/compression/zlib/contrib/iostream3/zfstream.cc

Purpose: implements the standard-compliant C++ gzip streambuf and stream classes used by iostream3.

Important APIs/types/functions: `gzfilebuf` constructor/destructor, `setcompression`, `open`, `attach`, `close`, `open_mode`, `showmanyc`, `underflow`, `overflow`, `setbuf`, `sync`, `enable_buffer`, `disable_buffer`; `gzifstream` and `gzofstream` constructors plus `open`, `attach`, and `close`.

Control flow: `open`/`attach` reject already-open and read-write modes, build a zlib mode string, call `gzopen`/`gzdopen`, enable buffers, and set ownership. Reads use `underflow()` to fill the get area from `gzread`. Writes use `overflow()` to append an optional char, flush the put area with `gzwrite`, or write a single char in unbuffered mode. `setbuf()` swaps external/internal buffers after syncing. `close()` syncs, calls `gzclose`, clears ownership, and disables buffers.

State and persistence: `gzfilebuf` tracks `gzFile`, open mode, fd ownership, buffer pointer/size, and buffer ownership. Files persist through zlib paths or descriptors.

Dependencies/integration: depends on `zfstream.h`, zlib `gz*`, standard `streambuf`, `cstring`, and `cstdio`.

Risks: simultaneous read/write and seeking are unsupported. `setcompression()` does not guard against null `file`. Unbuffered mode still allocates a one-byte get buffer. Destructor syncs before closing, so write errors during destruction cannot be reported to callers.

Test signals: `test.cc` and CMake shared/static tests exercise buffered/unbuffered read/write and compression manipulation.

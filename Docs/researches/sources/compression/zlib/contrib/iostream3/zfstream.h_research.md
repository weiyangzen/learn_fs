# sources/compression/zlib/contrib/iostream3/zfstream.h

Purpose: declares the modern iostream3 gzip stream buffer, input/output streams, and compression manipulator.

Important APIs/types/functions: class `gzfilebuf` deriving from `std::streambuf`; classes `gzifstream` and `gzofstream`; template `gzomanip2<T1,T2>`; inline `setcompression(gzofstream&, int, int)` and `setcompression(int, int)`.

Control flow: consumers use `gzifstream`/`gzofstream` similarly to standard file streams, call `open` or `attach`, stream formatted data, and optionally insert `setcompression(level, strategy)` into output streams. `rdbuf()` exposes the underlying buffer for `pubsetbuf()` and state checks.

State and persistence: private `gzfilebuf` fields declare the underlying `gzFile`, open mode, descriptor ownership, buffer pointer, buffer size, and buffer ownership. Stream classes embed one buffer each.

Dependencies/integration: includes `<istream>`, `<ostream>`, and `zlib.h`. Implemented by `zfstream.cc` and built by `iostream3` CMake targets.

Risks: no namespace is used, so symbols are global. Header comments note unsupported seeking, putback, and read/write access. `rdbuf()` returns a non-const pointer through `const_cast`, allowing mutation from const stream objects.

Test signals: direct CTest builds include this header in both library and executable targets; runtime smoke tests use open, close, `pubsetbuf`, and `setcompression`.

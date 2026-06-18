# sources/compression/zlib/contrib/iostream3/test.cc

Purpose: exercises iostream3 `gzofstream` and `gzifstream` for buffered and unbuffered gzip file I/O.

Important APIs/types/functions: `main`, `gzofstream`, `gzifstream`, `setcompression(Z_NO_COMPRESSION)`, `pubsetbuf(0,0)`, and `rdbuf()->in_avail()`.

Control flow: writes a formatted message to `test1.txt.gz`, prints the expected text, reads it back line by line with buffered input, then switches output and input buffers to unbuffered mode, writes the same message with no compression to `test2.txt.gz`, and reads it back.

State and persistence: creates `test1.txt.gz` and `test2.txt.gz` in the test working directory. CMake cleanup removes them later.

Dependencies/integration: depends on `zfstream.h`, the built iostream3 library, and zlib gzip behavior.

Risks: this is primarily a smoke test and prints output instead of asserting exact contents. It assumes current directory is writable. Resource-lock naming in CMake has a typo but still serializes consistently if shared.

Test signals: CTest builds and runs this executable for shared and static variants when enabled.

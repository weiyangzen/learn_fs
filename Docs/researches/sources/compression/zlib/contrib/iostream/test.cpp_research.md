# sources/compression/zlib/contrib/iostream/test.cpp

Purpose: demonstrates the original pre-standard C++ `gzofstream` stream wrapper by writing gzip data to standard output.

Important APIs/types/functions: `main()`, `gzofstream os(1, ios::out)`, `setcompressionlevel(Z_NO_COMPRESSION)`, and `setcompressionlevel(os, Z_DEFAULT_COMPRESSION)`.

Control flow: the program attaches a gzip output stream to file descriptor 1, writes one compressed line, changes the compression level to no compression for another line, changes back to default compression, writes a final line, closes the stream, and exits.

State and persistence: no persistent files. Output is written to stdout and can be piped to `zcat`.

Dependencies/integration: depends on `zfstream.h`, old `<fstream.h>`/iostream APIs, and zlib constants.

Risks: this is a demo, not a regression test. It assumes stdout can carry binary gzip data and that consumers will not treat it as text. The old iostream API may not build on modern C++ compilers.

Test signals: manual signal is `test | zcat` showing the expected text. The Makefile does not wire this specific demo into an automated target.

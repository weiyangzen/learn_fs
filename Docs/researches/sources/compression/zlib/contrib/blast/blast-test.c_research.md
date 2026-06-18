# sources/compression/zlib/contrib/blast/blast-test.c

Purpose: command-line example/test program for the `blast()` decompressor.

Important functions: `inf` reads up to `CHUNK` bytes from a `FILE *` into a static buffer; `outf` writes a buffer to a `FILE *`; `main` invokes `blast(inf, stdin, outf, stdout, &left, NULL)`.

Control flow: decompresses stdin to stdout, reports nonzero blast errors to stderr, drains any leftover input bytes to count unused data, reports a warning if leftovers exist, and returns the blast error code.

State and persistence: uses a static input buffer and standard streams only; no files are opened directly.

Dependencies and integration: includes `blast.h` and standard I/O. Used by the Makefile and CMake tests with `test.pk` and `test.txt`.

Risks: static input buffer makes `inf` non-reentrant. The program is intended as a single-stream filter and does not set binary mode on Windows by itself.

Test signals: nonzero process exit indicates decompressor error; output comparison in tests verifies decompressed bytes.

# sources/compression/zlib/contrib/puff/pufftest.c

Purpose: Command-line example and test driver for `puff()`. It reads raw DEFLATE data from a file or stdin, optionally skips wrapper bytes, determines inflated size, and optionally writes inflated bytes to stdout.

Important APIs, types, and functions: `bythirds()` grows input buffers by roughly the cube root of two to limit allocation slack. `load()` reads the entire stream into heap memory. `main()` parses `-w`, `-f`, and `-nnn`, calls `puff(NIL, ...)` for sizing, and calls `puff(dest, ...)` for output.

Control flow: Arguments are validated first. Input is loaded entirely, skip is applied, and a sizing inflate is attempted. On success it reports decompressed length and unused compressed bytes. With `-w` or `-f`, it allocates an output buffer and inflates again; `-f` halves the destination length to intentionally trigger output-space failure for coverage.

State and persistence: Uses heap buffers for input and optional output, frees them before exit, and writes diagnostics to stderr. It changes stdout to binary mode on DOS/Windows-like platforms before writing bytes.

Dependencies and integration points: Includes `stdio.h`, `stdlib.h`, and `puff.h`; conditionally includes `fcntl.h` and `io.h`. CMake tests compile it against puff shared/static libraries and coverage variants.

Risks: Entire input is loaded into memory, so it is unsuitable for unbounded streams. Return code is the raw `puff()` result, including negative values that shells may map modulo 256. The second inflate ignores its return value after the coverage/fail path.

Test signals: `tester.cmake` runs it on `zeros.raw`; `tester-cov.cmake` pipes crafted byte strings through this executable and checks exact process exit codes.

# sources/compression/lz4/tests/Makefile

Purpose: builds LZ4 test programs and orchestrates integration, platform, ABI, install, memory, fuzzer, frame, benchmark, and CLI tests.

Important targets/variables: configures `LIBDIR`, `PRGDIR`, flags, includes, `LZ4`, `TEST_FILES`, `FUZZER_TIME`, and `NB_LOOPS`; builds `fullbench`, `fuzzer`, `frametest`, `roundTripTest`, `datagen`, `checkFrame`, decompression partial tests, `abiTest`, and `checkTag`.

Control flow: shared make definitions generate C program recipes; POSIX-only tests compose shell scripts and data pipelines. Aggregate targets include `test-lz4-essentials`, `test-lz4`, `test`, `test32`, `test-mem`, `test-platform`, and `test-freestanding`.

State and persistence: creates binaries, objects, symlinks, `tmp*` files, version test directories, and `lz4_all.c`; `clean` removes generated artifacts and delegates clean to library/program dirs.

Dependencies/integration: uses library/program sources, Python tests, shell scripts, QEMU, valgrind, md5 tools, and installed library checks.

Risks: environment/toolchain-dependent 32-bit/QEMU/valgrind paths; temporary-file naming discipline matters; recursive make must preserve user variables.

Test signals: central map for compression/decompression, parser, dictionary, sparse, skippable, content-size, huge-file, ABI, CMake install, memory, and release checks.

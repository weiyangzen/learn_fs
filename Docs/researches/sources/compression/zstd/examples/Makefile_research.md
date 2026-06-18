# sources/compression/zstd/examples/Makefile

Purpose: builds and smoke-tests the zstd example programs against the local static library. It demonstrates one-shot, dictionary, streaming, multi-file, and memory-usage APIs.

Important targets: `all`, `$(LIB)`, each example binary target, `clean`, and `test`. `LIBDIR=../lib`, `CPPFLAGS += -I$(LIBDIR)`, and `LIB=$(LIBDIR)/libzstd.a` are central integration variables.

Control flow: `all` builds all listed example executables. Each object depends on `common.h`, and each binary depends on the static library. The library target recursively invokes `make -C ../lib libzstd.a`. `test` copies sample files, runs simple compression/decompression, multiple-file examples, streaming decompression, memory usage checks, invalid-input negative tests, zero-size file round trip, streaming multi-file compression, and dictionary compression/decompression.

State and persistence: generated executables, `.o` files, `tmp*`, `result*`, and `.zst` files are local build/test outputs. `clean` removes them.

Dependencies/integration: GNU make, local zstd library Makefile, C compiler/linker defaults, and `README.md`/`Makefile` as test inputs. It relies on shell `!` for expected-failure checks.

Risks: a new example must be added in several places to build and clean. The test suite mutates temporary files in the examples directory and can overwrite matching `tmp*` or `.zst` files. The threaded thread-pool example is not included in `all` here, despite being present in the directory.

Test signals: `make -C examples test`, negative invalid-input commands must fail, zero-byte compression must pass, and every binary should link against the local `libzstd.a`.

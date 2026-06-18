# sources/compression/zstd/tests/regression/Makefile

Purpose: This Makefile builds the zstd compression regression executable in `tests/regression`. It compiles the harness modules, links against a locally built multithreaded `libzstd.a`, and pulls in libcurl for downloading regression datasets.

Important targets and variables: `CFLAGS ?= -O3` allows callers to override optimization. `CURL_CFLAGS` and `CURL_LDFLAGS` come from `curl-config`; `CURL_LDFLAGS` also adds `-pthread`. `PROGDIR` and `LIBDIR` point to zstd's `programs` and `lib` directories. `ZSTD_CPPFLAGS` exposes program and library headers and suppresses deprecated API warnings because the harness intentionally exercises older APIs. Targets build `xxhash.o`, `util.o`, `data.o`, `config.o`, `method.o`, `result.o`, `test.o`, `libzstd.a`, and finally `test`.

Control flow: The default target is `all: test`. Object targets compile local and upstream source files with the regression flags. The phony `libzstd.a` target invokes `make -C ../../lib libzstd.a-mt` then copies the resulting archive into the regression directory. `test` links all objects and the archive with curl and pthread flags. `clean` delegates library cleanup and removes generated regression objects, archive, and executable.

State and persistence: Build outputs are local object files, copied `libzstd.a`, and `test`. No test data cache is managed here; runtime cache handling lives in `data.c` and the executable arguments.

Dependencies and integration points: Requires a C compiler, zstd source tree layout, `curl-config`, libcurl development files, pthread support, and make support in the upstream `lib` directory. It integrates harness modules through their headers and links static zstd plus `xxhash` and `util`.

Risks and test signals: `curl-config` is evaluated at make parse time, so missing curl tooling fails early or yields bad flags. Copying `libzstd.a` into the working directory can leave stale artifacts if the library target fails partially. A successful build produces the `test` executable; a useful smoke signal is `make -C tests/regression test`.

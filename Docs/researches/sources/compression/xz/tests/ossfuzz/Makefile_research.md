# sources/compression/xz/tests/ossfuzz/Makefile

Purpose: minimal OSS-Fuzz build recipe for fuzz targets in the `tests/ossfuzz` directory.

Important targets: `FUZZ_TARGET_SRCS` discovers all `.c` files, `FUZZ_TARGET_BINS` strips suffixes, `all` builds each target, pattern rule `%: %.c` compiles C to object with liblzma API includes and links with `$(CXX)`, `$(LIB_FUZZING_ENGINE)`, and static `liblzma.a`. `clean` removes local objects but leaves binaries under `$(OUT)`.

Control flow: OSS-Fuzz supplies compiler variables, fuzzing engine, and `OUT`. Each target is built independently from one C file plus shared header code.

State and persistence: creates object files in the source directory and fuzz target binaries in `$(OUT)`. `clean` intentionally does not remove `$(OUT)` artifacts because the fuzzing framework owns them.

Dependencies and integration: depends on a prebuilt `../../src/liblzma/.libs/liblzma.a`, liblzma API headers, and OSS-Fuzz environment variables.

Risks: wildcard discovery will build every `.c` file in the directory; adding helper `.c` files would accidentally create targets. The Makefile assumes liblzma has already been built in the expected relative path.

Test signals: successful build produces one binary per fuzz source. Runtime signal comes from fuzzers aborting on `LZMA_PROG_ERROR` or target initialization failures.

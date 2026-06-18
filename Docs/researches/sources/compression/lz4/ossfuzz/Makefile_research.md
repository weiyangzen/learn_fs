# sources/compression/lz4/ossfuzz/Makefile

## Purpose
This Makefile builds the LZ4 OSS-Fuzz targets either against libFuzzer through `LIB_FUZZING_ENGINE` or against the local standalone engine when that variable is empty.

## Important APIs, Types, And Functions
The main targets are the ten `*_fuzzer` binaries: block compression/decompression, HC variants, frame variants, round-trip variants, uncompressed frame update, and streaming. It builds `../lib/liblz4.a`, compiles each C file, and links common helper objects `lz4_helpers.o` and `fuzz_data_producer.o`.

## Control Flow
`all` expands to all fuzzers. Pattern rules compile `%.c` to `%.o` with LZ4 include paths, `LZ4_DEBUG`, `XXH_NAMESPACE=LZ4_`, and `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`. If no external fuzzing engine is supplied, `standaloneengine.o` is linked so corpus files can be run from the command line.

## State, Persistence, And Dependencies
Build outputs are local object files, fuzzer executables, and the static liblz4 archive. The Makefile consumes standard `CC`, `CXX`, `CFLAGS`, `CXXFLAGS`, `CPPFLAGS`, `LDFLAGS`, `EXT`, and `MOREFLAGS`.

## Integration Points
`ossfuzz.sh` invokes `make V=1 all` from this directory. The OSS-Fuzz project supplies compiler wrappers and `LIB_FUZZING_ENGINE`, while local development can use the standalone fallback.

## Risks
The clean target omits `round_trip_frame_uncompressed_fuzzer_clean`, leaving that binary or object behind. Helper objects are linked into every fuzzer even when a target does not use all helpers. Assertions are enabled through `LZ4_DEBUG`, so behavior differs from release builds.

## Test Signals
`make all`, `make clean`, builds with and without `LIB_FUZZING_ENGINE`, sanitizer builds, and one standalone corpus invocation for each fuzzer validate the file.

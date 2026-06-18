# sources/compression/lz4/examples/Makefile

## Purpose
The examples Makefile builds and tests LZ4 sample programs against a local static `liblz4.a`. It demonstrates the library's block, frame, file, streaming, dictionary, and benchmarking APIs.

## Important Targets and Variables
`LIBDIR`, `LIBLZ4DIR`, `LIBLZ4SRCS`, `LIBLZ4OBJS`, and `SLIBLZ4` define the local static library. `ALL` lists the example programs: `print_version`, `simple_buffer`, `frameCompress`, `fileCompress`, `blockStreaming_doubleBuffer`, `blockStreaming_ringBuffer`, `streamingHC_ringBuffer`, `blockStreaming_lineByLine`, `dictionaryRandomAccess`, and `bench_functions`. `test` builds examples and the CLI under `../programs/lz4`, runs each sample, validates `.lz4` outputs with `lz4 -vt`, and runs a quick benchmark.

## Control Flow
The file includes `../build/make/multiconf.make`, uses its `static_library` helper to create `liblz4.a`, builds all example binaries, then `test` runs examples in a fixed order against `Makefile` and `.gitignore`.

## State and Persistence
Build artifacts include object files, `liblz4.a`, example binaries, compressed files, decoded files, and streaming sample files. `clean` removes these generated outputs.

## Dependencies and Integration Points
It depends on the LZ4 library source files, build helper makefiles, a C compiler, and the `../programs/lz4` CLI for validation. The examples include headers from `../lib`.

## Risks
The examples intentionally write output files beside the test inputs and use fixed suffixes; stale files can obscure failures if not cleaned. Some tests rely on `.gitignore` existing as a small file. The benchmark is timing-sensitive and should not be used as a strict performance regression gate without stronger controls.

## Test Signals
`make -C examples test` is the primary signal. Expected markers include `Verify : OK`, `verify : OK`, successful `lz4 -vt` verification, and `All done` from `bench_functions`.

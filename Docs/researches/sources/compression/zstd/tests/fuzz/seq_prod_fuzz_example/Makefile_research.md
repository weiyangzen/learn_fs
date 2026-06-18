# sources/compression/zstd/tests/fuzz/seq_prod_fuzz_example/Makefile

## Purpose

This Makefile builds the example third-party sequence producer object used to demonstrate the custom sequence-producer fuzzing interface. It intentionally produces only `example_seq_prod.o`, which can be passed to `fuzz.py --custom-seq-prod=...`.

## Important Targets And Variables

`CC` defaults to `clang`. `CFLAGS` includes debug info, frame pointers, undefined/address/fuzzer sanitizers, and include paths for the parent fuzz directory and zstd library headers. The `default` phony target depends on `example_seq_prod.o`; that object target compiles `example_seq_prod.c` with `$(CC) -c $(CFLAGS)`.

## Control Flow

Running `make` in the directory builds the object file. There is no link step, clean target, dependency generation, or sanitizer variant matrix.

## State And Persistence

The build output is the local object file `example_seq_prod.o`. No generated sources or persistent test records are created.

## Dependencies And Integration Points

The file assumes clang and sanitizer/fuzzer runtime support are available. Its include paths align with `fuzz_third_party_seq_prod.h` documentation and zstd's `tests/fuzz` and `lib` directories. The resulting object integrates with zstd fuzz builds through `fuzz.py`.

## Risks And Edge Cases

The flags are demonstration-oriented and may not match every platform. GCC is not supported for this plugin path per the header guidance. Because only an object file is built, ABI compatibility depends on using matching compiler and sanitizer options when building the main fuzzer binaries.

## Test Signals

Successful `make` should produce a sanitizer-instrumented `example_seq_prod.o`. The stronger test is linking that object into a fuzzer build with `--custom-seq-prod` and confirming the example producer hooks run without link errors or sanitizer findings.

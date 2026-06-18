# sources/compression/zstd/tests/fuzz/fuzz_third_party_seq_prod.h

## Purpose

`fuzz_third_party_seq_prod.h` defines the optional plugin ABI that lets external zstd sequence-producer implementations be linked into zstd fuzzers. It documents how a plugin author supplies setup, teardown, state allocation, state free, and sequence production symbols that replace the default test producer when `FUZZ_THIRD_PARTY_SEQ_PROD` is enabled.

## Important APIs And Types

The required plugin hooks are `FUZZ_seqProdSetup()`, `FUZZ_seqProdTearDown()`, `FUZZ_createSeqProdState()`, `FUZZ_freeSeqProdState()`, and `FUZZ_thirdPartySeqProd()`. The producer signature matches `ZSTD_sequenceProducer_F`: it receives a plugin state pointer, output `ZSTD_Sequence` array and capacity, source and dictionary buffers, compression level, and window size.

`FUZZ_SEQ_PROD_SETUP()` and `FUZZ_SEQ_PROD_TEARDOWN()` are internal harness macros. When `FUZZ_THIRD_PARTY_SEQ_PROD` is defined, setup asserts successful global setup and non-NULL state creation, storing the result in `FUZZ_seqProdState`; teardown asserts state destruction and global teardown success. When the macro is not defined, both expand to no-ops.

## Control Flow

Fuzz targets call `FUZZ_SEQ_PROD_SETUP()` near the start of `LLVMFuzzerTestOneInput()` and `FUZZ_SEQ_PROD_TEARDOWN()` before returning. The actual producer is registered by helper code through `ZSTD_registerSequenceProducer()`, using the state pointer created here. The header assumes each test case uses one shared state object and notes that current fuzzers do not exercise multi-threaded sequence-producer scenarios.

## State And Persistence

The harness-level persistent object is `FUZZ_seqProdState`, declared in `zstd_helpers.h` only under `FUZZ_THIRD_PARTY_SEQ_PROD` and defined by `zstd_helpers.c`. Plugin implementations may also hold global or external resources between setup and teardown. State must be reclaimed per test case to avoid leak accumulation during fuzzing.

## Dependencies And Integration Points

This header requires `ZSTD_STATIC_LINKING_ONLY` and `zstd.h` for the unstable sequence producer API and `ZSTD_Sequence` type. It integrates with `fuzz.py` via `--custom-seq-prod=...`, with libFuzzer/ASan/UBSan builds, and with zstd compression contexts through `ZSTD_registerSequenceProducer()`.

## Risks And Edge Cases

The ABI is intentionally narrow but fragile: plugin code must be built with compatible compiler and sanitizer settings, and setup/state hooks must return exact success values expected by the macros. Multi-threaded use is explicitly not covered. If a producer returns malformed sequences or mishandles dictionaries/window sizes, downstream fuzzers should either validate fallback behavior or expose compressor bugs.

## Test Signals

Successful custom-producer fuzzing should show setup and teardown executing for every test case, non-NULL state creation, registration into compression contexts, and fallback behavior when the producer returns `ZSTD_SEQUENCE_PRODUCER_ERROR`. Sanitizer builds are the primary signal for plugin memory/thread-safety issues.

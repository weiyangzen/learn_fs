# sources/compression/zstd/tests/fuzz/zstd_helpers.c

## Purpose

`zstd_helpers.c` implements shared zstd-specific fuzz helper logic: randomized compression/frame parameter generation, installation of random parameters onto a `ZSTD_CCtx`, optional sequence-producer registration, and quick dictionary training for dictionary fuzz targets.

## Important APIs And Functions

It defines `kMinClevel = -3`, `kMaxClevel = 19`, and `void* FUZZ_seqProdState`. Internal helpers `set()`, `produceParamValue()`, and `setRand()` wrap `ZSTD_CCtx_setParameter()` with fuzz assertions. Public helpers are `FUZZ_randomCParams()`, `FUZZ_randomFParams()`, `FUZZ_randomParams()`, `FUZZ_setRandomParameters()`, and `FUZZ_train()`.

`setSequenceProducerParams()` registers either `FUZZ_thirdPartySeqProd()` with `FUZZ_seqProdState` when `FUZZ_THIRD_PARTY_SEQ_PROD` is defined, or zstd's `simpleSequenceProducer` otherwise. It also configures sequence-producer fallback, disables workers, and disables long-distance matching for that producer mode.

## Control Flow

Random parameter generation consumes deterministic bytes from `FUZZ_dataProducer_t`, first choosing compression parameters within bounded low-to-moderate ranges and passing them through `ZSTD_adjustCParams()`, then choosing frame flags. `FUZZ_setRandomParameters()` writes many zstd compression parameters onto a context, including LDM settings, threading/rsyncable behavior, row matcher, dictionary attach behavior, block splitter, target block size, max block size, validation, repcode resolution, and optional source-size hint.

When zstd is built without multithreading, it still consumes entropy for worker and rsyncable choices before forcing both settings to zero, keeping corpus interpretation reproducible across builds. Sequence producer registration is mandatory under `FUZZ_THIRD_PARTY_SEQ_PROD` and randomly enabled otherwise.

`FUZZ_train()` creates synthetic samples from random offsets in the source, fills unused sample bytes with zeros, configures fastCover parameters, and calls `ZDICT_trainFromBuffer_fastCover()`. On training error, it frees the dictionary buffer and returns a zeroed dictionary struct.

## State And Persistence

`FUZZ_seqProdState` is global state shared with the third-party sequence producer macros. The helper functions otherwise mutate caller-owned compression contexts. `FUZZ_train()` returns heap memory owned by the caller on success. Parameter generation depends on the producer cursor, so helper call order is part of the fuzz contract.

## Dependencies And Integration Points

This file requires `ZSTD_STATIC_LINKING_ONLY` and `ZDICT_STATIC_LINKING_ONLY`, zstd/zdict APIs, `sequence_producer.h`, fuzz helpers, and the third-party sequence producer header. It is linked into many fuzz targets in this directory and controls a large share of their parameter-space coverage.

## Risks And Edge Cases

Because the helper sets many experimental/static-only parameters, changes in zstd parameter bounds can make fuzzers start failing during setup. Cross-build reproducibility depends on consuming entropy even when features such as multithreading are compiled out. Sequence-producer fallback settings differ between built-in and third-party modes and must stay aligned with fuzzer expectations. `FUZZ_train()` must handle tiny or empty sources carefully via `MAX(srcSize, 1) - 1` and zero-sized sample slices.

## Test Signals

Fuzz targets using this helper should continue to reproduce corpus behavior across builds with and without `ZSTD_MULTITHREAD`. Unit-level signals include valid adjusted compression parameters, successful context parameter setting, correct sequence-producer fallback registration, and dictionary training returning either a valid buffer or a clean zeroed result.

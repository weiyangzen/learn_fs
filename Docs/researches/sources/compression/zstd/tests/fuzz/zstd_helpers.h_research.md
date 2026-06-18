# sources/compression/zstd/tests/fuzz/zstd_helpers.h

## Purpose

`zstd_helpers.h` declares the shared zstd fuzz helper API implemented by `zstd_helpers.c`. It exposes randomized parameter generation, context parameter installation, quick dictionary training, shared compression level bounds, and optional third-party sequence producer state.

## Important APIs And Types

The header declares `kMinClevel`, `kMaxClevel`, `FUZZ_setRandomParameters()`, `FUZZ_randomCParams()`, `FUZZ_randomFParams()`, and `FUZZ_randomParams()`. It defines `FUZZ_dict_t` as a simple `{ void* buff; size_t size; }` pair returned by `FUZZ_train()`.

When `FUZZ_THIRD_PARTY_SEQ_PROD` is defined, it declares `extern void* FUZZ_seqProdState`, allowing setup macros and helper registration code to share the per-test-case state pointer.

## Control Flow

The header has no direct runtime behavior. It enables fuzz targets to request randomized context setup before compression and to request fast dictionary training from an input buffer.

## State And Persistence

The only declared shared state is `FUZZ_seqProdState` under the third-party producer build. `FUZZ_dict_t` ownership is by convention: callers that receive a nonzero dictionary from `FUZZ_train()` must free `buff` when done.

## Dependencies And Integration Points

It enables `ZSTD_STATIC_LINKING_ONLY` before including `zstd.h`, includes `zstd_errors.h`, and depends on `fuzz_data_producer.h`. It is included by most zstd compression fuzz targets and provides the stable local contract for randomized parameter coverage.

## Risks And Edge Cases

Because the header exposes static-linking-only zstd types and parameters, it is tied to internal/experimental zstd API stability. Callers must treat `FUZZ_train()` as fuzz-only dictionary generation, not production training, and must account for failed training returning an empty struct.

## Test Signals

Compile coverage across fuzz targets is the primary signal for this header. Runtime signals come from successful parameter application, reproducible corpus behavior, and correct dictionary ownership in targets using `FUZZ_train()`.

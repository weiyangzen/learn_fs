# sources/compression/zstd/tests/fuzz/seq_prod_fuzz_example/example_seq_prod.c

## Purpose

`example_seq_prod.c` is a minimal implementation of the third-party sequence producer ABI. It demonstrates setup/teardown, state allocation, shared-state checking, and producer fallback behavior for fuzzing custom sequence producers.

## Important APIs And Functions

It implements all symbols declared by `fuzz_third_party_seq_prod.h`: `FUZZ_seqProdSetup()`, `FUZZ_seqProdTearDown()`, `FUZZ_createSeqProdState()`, `FUZZ_freeSeqProdState()`, and `FUZZ_thirdPartySeqProd()`. It uses `_Thread_local size_t threadLocalState` and a heap-allocated `size_t` shared state.

`FUZZ_thirdPartySeqProd()` receives the full sequence producer signature but only checks state consistency, increments shared and thread-local counters, and returns `ZSTD_SEQUENCE_PRODUCER_ERROR`.

## Control Flow

Setup resets the thread-local counter to zero. State creation allocates a zeroed `size_t`; free releases it. Each producer invocation asserts the shared state equals the thread-local state, increments both, then returns the special sequence-producer error to force zstd's fallback path when fallback is enabled.

## State And Persistence

The example intentionally uses both thread-local state and shared state to catch unsafe reuse across unexpected threading or lifecycle boundaries. The shared state is per fuzz test case, and the thread-local counter is reset at setup. No dictionary/source data is inspected.

## Dependencies And Integration Points

It depends on `fuzz_third_party_seq_prod.h`, which brings in zstd static APIs and `ZSTD_Sequence`. It is compiled to an object file by the adjacent Makefile and linked into fuzzers that define `FUZZ_THIRD_PARTY_SEQ_PROD`.

## Risks And Edge Cases

The example is not a real producer; it always requests fallback. Its assertions assume single-threaded invocation and ordered setup before production. If future fuzzers exercise sequence producers concurrently, this file is expected to expose that mismatch rather than support it.

## Test Signals

A linked fuzzer should call the producer repeatedly, maintain matching counters, and successfully fall back to zstd's built-in compression behavior. Assertion failures indicate lifecycle or threading changes in the sequence-producer integration.

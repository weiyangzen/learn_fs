# sources/compression/zstd/tests/external_matchfinder.c

## Purpose
This file provides a test sequence producer for zstd's external matchfinder/sequence producer API. It can emit valid simple sequences or intentionally invalid/error cases.

## APIs, functions, and control flow
`simpleSequenceProducer()` implements a small hash-table match finder over the current source using `ZSTD_hashPtr()` and `ZSTD_count()`, emitting `ZSTD_Sequence` entries when matches are within `windowSize` and finishing with a final literals-only sequence. `zstreamSequenceProducer()` is the exported callback; it reads an `EMF_testCase` from `sequenceProducerState`, zeroes the output buffer, and switches among cases: zero sequences, one big literals sequence, many valid sequences, invalid offset/match/literal lengths, invalid final literals, capacity+1 small error, or `ZSTD_SEQUENCE_PRODUCER_ERROR`.

## State, dependencies, risks, and test signals
State is callback-local except for constants `HLOG`, `MLS`, and `BADIDX`. The file depends on `external_matchfinder.h`, `zstd_compress_internal.h`, and the static-linking zstd sequence API. Risks include ignoring `outSeqsCapacity` in several paths and assuming `srcSize` is large enough for invalid-case arithmetic; those are deliberate stress behaviors but dangerous if reused outside tests. Test signals come from consumers verifying accepted valid sequences and rejected invalid producer outputs.

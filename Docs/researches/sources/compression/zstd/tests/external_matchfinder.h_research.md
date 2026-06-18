# sources/compression/zstd/tests/external_matchfinder.h

## Purpose
This header declares the external matchfinder test cases and the sequence producer callback used by zstd tests.

## APIs and integration
It defines `EMF_testCase` values for valid and invalid producer behaviors and declares `zstreamSequenceProducer()` with the `ZSTD_sequenceProducer_F` compatible signature. It defines `ZSTD_STATIC_LINKING_ONLY` before including `zstd.h` so `ZSTD_Sequence` and advanced APIs are visible.

## State, risks, and test signals
The header contains no state. Its risk is API coupling to static zstd definitions and enum/order coupling with test callers. Correct integration is signaled by test code being able to pass enum values as callback state and observe expected compression API behavior.

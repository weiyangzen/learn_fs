# sources/compression/zstd/tests/fuzz/fuzz_data_producer.c

## Purpose
This file implements the byte-stream data producer used by fuzz targets to derive randomized parameters from the same input as payload data.

## APIs, functions, and control flow
`FUZZ_dataProducer_create()` allocates a producer with `data`, `size`, and current read position semantics; `FUZZ_dataProducer_free()` releases it. The implementation provides byte consumption primitives through macros/templates in the included header path and exported functions for `remainingBytes`, `rollBack`, `empty`, `contract`, and `reserveDataPrefix`. `contract()` reduces the producer's active size, while `reserveDataPrefix()` leaves a prefix for target payload and uses the suffix for parameter generation.

## State, dependencies, risks, and test signals
State is one heap allocation per producer plus immutable references into the fuzz input. Dependencies are standard allocation and assertions in fuzz helpers. Risks are off-by-one cursor arithmetic and callers misunderstanding whether consumed bytes come from the front or back. Test signals are deterministic parameter derivation from a given input and sanitizer-clean operation when targets consume many parameter types.

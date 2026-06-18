# sources/compression/zstd/tests/fuzz/fuzz_data_producer.h

## Purpose
This header exposes the fuzz data producer abstraction for turning input bytes into bounded integers, booleans, and reserved payload slices.

## APIs and integration
It forward-declares `FUZZ_dataProducer_t` and declares lifecycle/control functions: `create`, `free`, `remainingBytes`, `rollBack`, `empty`, `contract`, and `reserveDataPrefix`. The header also provides typed producer helpers/macros used by targets, such as integer-range selection, so fuzz inputs can choose compression levels, buffer sizes, dictionary sizes, and streaming chunk sizes reproducibly.

## State, dependencies, risks, and test signals
The header itself has no state but defines the contract for producer cursor state in the `.c` file. Risks include range helpers being called with invalid min/max values and target code depending on byte consumption order. Correctness is signaled by deterministic reproduction: the same fuzz input must derive the same parameter sequence.

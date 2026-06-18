# sources/compression/lz4/ossfuzz/fuzz_data_producer.h

## Purpose
This header declares the `FUZZ_dataProducer_t` abstraction used by fuzzers to consume deterministic configuration bytes from fuzz input.

## Important APIs, Types, And Functions
It forward-declares `FUZZ_dataProducer_t` and exposes creation, destruction, `FUZZ_dataProducer_retrieve32()`, `FUZZ_getRange_from_uint32()`, `FUZZ_dataProducer_range32()`, `FUZZ_dataProducer_preferences()`, `FUZZ_dataProducer_frameInfo()`, and `FUZZ_dataProducer_remainingBytes()`.

## Control Flow
There is no runtime control flow in the header. Its comments define the expected use: construct from input, retrieve control values, use remaining bytes as payload, then free the producer.

## State, Persistence, And Dependencies
The state layout is hidden in the `.c` file. The header includes standard integer and allocation headers plus `fuzz_helpers.h`, `lz4frame.h`, and `lz4hc.h` so preference-returning functions have complete types.

## Integration Points
Compression, HC, frame, decompression, and round-trip fuzzers include this header to share the same deterministic control-value generation.

## Risks
There are no include guards, so repeated inclusion relies on the included headers' guards and can still redeclare prototypes benignly. The API name `retrieve32` implies more entropy than the implementation currently provides. Callers may misread `remainingBytes()` as advancing `data`, but it only changes the size.

## Test Signals
Build coverage for repeated inclusion, C++ inclusion through wrappers, and behavior tests paired with the implementation are the main signals.

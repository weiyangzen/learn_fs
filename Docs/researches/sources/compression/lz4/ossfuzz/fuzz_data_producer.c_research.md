# sources/compression/lz4/ossfuzz/fuzz_data_producer.c

## Purpose
`fuzz_data_producer.c` implements a small deterministic input-consumption helper. Fuzz targets use it to derive sizes, compression levels, and frame preferences from the end of the input while preserving the remaining bytes as payload.

## Important APIs, Types, And Functions
The private `FUZZ_dataProducer_s` stores `data` and remaining `size`. Public functions create/free a producer, retrieve a 32-bit-ish seed, map seeds into inclusive ranges, build `LZ4F_frameInfo_t`, build `LZ4F_preferences_t`, and report remaining bytes.

## Control Flow
`FUZZ_dataProducer_retrieve32()` consumes from the tail. Empty input yields zero, inputs shorter than four bytes consume one byte, and inputs of at least four bytes subtract four from `size`. Range generation handles the full 32-bit span specially; otherwise it returns `min + seed % (range + 1)`. Frame preference generation derives block size, block mode, checksums, compression level, auto-flush, and decompression-speed preference.

## State, Persistence, And Dependencies
State is only the mutable remaining-size counter and the original data pointer. The helper allocates its state with `malloc` and frees it with `free`.

## Integration Points
Most OSS-Fuzz targets use this helper instead of `FUZZ_seed()` when they need several deterministic control values. It depends on `fuzz_helpers.h`, `lz4frame.h`, and `lz4hc.h`.

## Risks
For inputs of at least four bytes, `retrieve32()` returns only `*(data + size - 4)`, not a full little-endian 32-bit value, so entropy is much lower than the function name suggests. It also does not advance the data pointer, so callers must remember that only `remainingBytes()` changes.

## Test Signals
Unit tests should cover empty, 1-3 byte, and 4+ byte retrieval; inclusive range boundaries; full-span ranges; and valid frame preferences across all enum ranges.

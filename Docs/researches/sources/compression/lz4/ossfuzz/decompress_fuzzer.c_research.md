# sources/compression/lz4/ossfuzz/decompress_fuzzer.c

## Purpose
This harness fuzzes raw LZ4 block decompression and partial decompression with no dictionary, external dictionaries, and prefix-style dictionaries.

## Important APIs, Types, And Functions
It calls `LZ4_decompress_safe_usingDict()`, `LZ4_decompress_safe_partial()`, and `LZ4_decompress_safe_partial_usingDict()` across small and large dictionary configurations. `MIN` and `MAX` come from `fuzz_helpers.h`.

## Control Flow
The producer selects destination capacity in `[0, 4 * size]`. The harness allocates a backing dictionary large enough to hold a 64 KB dictionary plus the fuzz data, copies the fuzz data after the dictionary, and then performs eleven decompression attempts over raw input and prefix-addressed input. Return codes are ignored because malformed compressed data is expected.

## State, Persistence, And Dependencies
State is limited to per-input destination and dictionary buffers. The dictionary is zero-filled, and the input is copied behind it to create prefix layouts.

## Integration Points
This target stresses the block decoder paths that must safely reject arbitrary compressed data. It is a counterpart to the block compressor and round-trip harnesses.

## Risks
The `dictSize` computation uses `MAX(size + 1, 64 KB - 1)`, so it may allocate substantially more than the minimum for large fuzz inputs. The harness is crash-focused and does not validate expected negative return codes. Allocation of zero-byte destination buffers is asserted.

## Test Signals
Relevant signals are crashes, sanitizer out-of-bounds reports, unsafe dictionary boundary handling, and partial-decompression bugs with prefix and external dictionaries.

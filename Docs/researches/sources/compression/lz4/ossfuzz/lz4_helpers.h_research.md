# sources/compression/lz4/ossfuzz/lz4_helpers.h

## Purpose
This header declares LZ4-specific helper functions shared by frame fuzzers.

## Important APIs, Types, And Functions
It declares `FUZZ_randomFrameInfo()`, `FUZZ_randomPreferences()`, and `FUZZ_decompressFrame()`. The first two take a mutable random seed; the decompression helper accepts destination buffer/capacity and source frame/size.

## Control Flow
There is no runtime control flow in the header. The include guard is `LZ4_HELPERS`, and `lz4frame.h` supplies frame types.

## State, Persistence, And Dependencies
The header stores no state. All state is owned by the implementation or caller. It depends on `uint32_t` being visible from prior includes in some translation units, because it includes `lz4frame.h` but not `stdint.h` directly.

## Integration Points
Frame fuzz targets include this header to avoid duplicating preference selection and strict decompression checks.

## Risks
The guard name is broad and could collide with unrelated code. Missing a direct `stdint.h` include makes the header less self-contained. `FUZZ_decompressFrame()`'s strict semantics should not be used for arbitrary input fuzzing where errors are expected.

## Test Signals
A standalone compile of this header, plus frame round-trip fuzz runs using each declared function, covers the expected behavior.

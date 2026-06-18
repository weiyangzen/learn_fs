# sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser_unittest.cc

## Purpose
This GoogleTest file verifies `ChunkFilenameParser` behavior for valid standard/XOR/EC chunk names and invalid filename variants.

## Important APIs, Types, And Functions
- `TEST(ChunkFilenameParser, ParseStandardChunkFilename)` checks standard `.liz` parsing and unsigned 64-bit chunk ids.
- `ParseXorChunkFilename`, `ParseXorChunkFilenameMaxLevel`, `ParseXorParityFilename`, and `ParseXorParityFilenameMaxLevel` validate XOR data/parity naming and format detection.
- `ParseECChunkFilename` and `ParseECChunkFilenameMaxLevel` validate EC naming.
- `ParseWrongFilenames` enumerates malformed names and expects `ERROR_INVALID_FILENAME`.

## Control Flow
Each test constructs a parser with one filename, calls `parse`, and asserts parsed format/id/version/type or error status. The invalid test runs a sequence of independent parser constructions.

## State And Persistence
No persistent state. Tests validate parsing rules that affect disk scan recognition.

## Dependencies And Integration Points
It depends on GoogleTest, `chunk_filename_parser.h`, and `slice_traits` constructors/constants for expected `ChunkPartType` values.

## Risks
The invalid EC leading-zero parity case duplicates the same string as the data-count case, so one intended invalid parity variation may be untested. The legacy `ec_` prefix accepted by implementation is not directly tested.

## Test Signals
This is the direct test signal for filename parsing. It has strong negative coverage for casing, length, trailing data, XOR ranges, missing parts, illegal characters, and EC ranges.

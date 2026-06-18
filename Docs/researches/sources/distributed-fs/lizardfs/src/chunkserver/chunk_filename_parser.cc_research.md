# sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser.cc

## Purpose
`chunk_filename_parser.cc` parses chunk file basenames into chunk format, chunk type, chunk id, and version. It supports standard, XOR, and EC naming, plus `.mfs` and `.liz` formats.

## Important APIs, Types, And Functions
- `ChunkFilenameParser::parse` parses the full filename and rejects trailing characters.
- `parseChunkType` detects `ec2_`, legacy `ec_`, `xor_`, or default standard chunk type.
- `parseECChunkType` parses `part_of_data_parity_` and validates EC data/parity counts and part index.
- `parseXorChunkType` parses data parts like `xor_1_of_3_` and parity parts like `xor_parity_of_3_`.
- `isUpperCaseHexDigit` enforces uppercase hexadecimal ids/versions.
- Accessors return `ChunkFormat`, `ChunkPartType`, version, and id after parsing.

## Control Flow
Parsing starts by assuming `ChunkFormat::INTERLEAVED`, consumes `chunk_`, parses an optional type prefix, then consumes exactly 16 uppercase hex digits for chunk id, an underscore, exactly 8 uppercase hex digits for version, and either `.liz` or `.mfs`. `.mfs` switches format to MooseFS. Any bad consume, invalid numeric range, leading zero in type counts, overlong XOR count, invalid EC part, lowercase hex, or trailing data returns `ERROR_INVALID_FILENAME`.

## State And Persistence
The parser holds parsed values in object fields. It does not persist state, but its acceptance rules define which on-disk files the chunkserver recognizes during scans.

## Dependencies And Integration Points
It depends on `common/parser.h`, `ChunkFormat`, `ChunkPartType`, `Goal`, and `slice_traits`. It must stay aligned with `Chunk::generateFilenameForVersion` and the storage scanner.

## Risks
- There are two accepted EC prefixes, `ec2_` and `ec_`, but filename generation currently emits `ec2_`; compatibility intent should remain clear.
- Parser strictness around uppercase hex and leading zeroes can cause valid-looking manual files to be ignored.
- C library character functions are used through predicates; inputs outside plain ASCII should not be expected.
- The exception catch has `std:: invalid_argument` spacing that compiles as `std::invalid_argument`, but it is visually odd.

## Test Signals
`chunk_filename_parser_unittest.cc` extensively covers standard, XOR, XOR parity, EC, `.mfs`, `.liz`, high unsigned chunk ids, and many invalid filename cases. Tests do not appear to cover the legacy `ec_` prefix directly.

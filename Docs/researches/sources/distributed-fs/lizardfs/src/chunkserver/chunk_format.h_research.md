# sources/distributed-fs/lizardfs/src/chunkserver/chunk_format.h

## Purpose
`chunk_format.h` defines the enum describing on-disk chunk file format.

## Important APIs, Types, And Functions
- `enum class ChunkFormat { IMPROPER, MOOSEFS, INTERLEAVED }`.

## Control Flow
The enum is used as a value returned by chunk classes and parsers. `MOOSEFS` corresponds to header-plus-data `.mfs` files; `INTERLEAVED` corresponds to data-plus-CRC block `.liz` files; `IMPROPER` is the base/default invalid format.

## State And Persistence
This enum directly models persisted file layout. Storage code uses it to choose offsets, validation, and filename extension.

## Dependencies And Integration Points
It includes `common/platform.h` and is included by `chunk.h`, `chunk.cc`, and `chunk_filename_parser`.

## Risks
Adding formats requires coordinated changes in parser, filename generation, chunk subclass behavior, signature/header handling, and tests.

## Test Signals
`chunk_filename_parser_unittest.cc` and `chunk_unittest.cc` indirectly validate format values for parsed/generated filenames.

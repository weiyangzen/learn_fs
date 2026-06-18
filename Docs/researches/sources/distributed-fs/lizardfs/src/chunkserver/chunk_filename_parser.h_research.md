# sources/distributed-fs/lizardfs/src/chunkserver/chunk_filename_parser.h

## Purpose
`chunk_filename_parser.h` declares the parser class for chunk file basenames.

## Important APIs, Types, And Functions
- `Status` reports `OK` or `ERROR_INVALID_FILENAME`.
- Constructor accepts a filename string and initializes the base `Parser`.
- `parse` performs full parsing.
- Accessors expose parsed `chunkFormat`, `chunkType`, `chunkVersion`, and `chunkId`.
- Private constants enforce 16 hex digits for chunk id and 8 for version.
- Private helpers split XOR, EC, and top-level type parsing.

## Control Flow
The class is stateful: construct, call `parse`, then read accessors if status is `OK`.

## State And Persistence
State is the parser cursor inherited from `Parser` plus parsed chunk fields. No persistence is performed, but the parsed output drives persisted chunk discovery.

## Dependencies And Integration Points
It includes `chunk_format.h`, `ChunkPartType`, and `Parser`. It is part of the storage scan/file-discovery path and is validated by its unit test.

## Risks
Accessors can be called after a failed parse and will return partially initialized/default values. Callers must check `Status`.

## Test Signals
The matching unittest covers the public parser behavior across valid and invalid names.

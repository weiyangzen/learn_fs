# sources/compression/lz4/tests/datagen.h

## Purpose
`datagen.h` declares the public interface for the compressible random data generator used by LZ4 test and benchmark programs.

## Important APIs, Types, and Functions
It exports `RDG_genOut(unsigned long long size, double matchProba, double litProba, unsigned seed)` and `RDG_genBuffer(void* buffer, size_t size, double matchProba, double litProba, unsigned seed)`. `RDG_genOut()` writes to stdout, while `RDG_genBuffer()` fills a supplied memory region.

## Control Flow, State, and Persistence
The header owns no state and performs no work. Its comments define the behavioral contract: `litProba` is optional, `0.0` selects a default derived from match probability, and equal parameters plus seed produce identical generated content.

## Dependencies and Integration Points
It includes only `<stddef.h>` for `size_t`. `datagen.c` implements these declarations and `datagencli.c` calls them when the CLI receives `-P`.

## Risks and Test Signals
The main risk is semantic drift between the comments and implementation, especially deterministic output and default literal probability. Compile-time users get a small, stable API surface with no exposed internal types.

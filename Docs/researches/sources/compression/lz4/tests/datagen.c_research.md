# sources/compression/lz4/tests/datagen.c

## Purpose
`datagen.c` implements the reproducible compressible data generator used by the LZ4 test tools. It can fill a caller-provided buffer or stream bytes to stdout while controlling match probability, literal distribution, and seed. The generated stream deliberately resembles LZ4-friendly data: short literals interleaved with back-references within a 32 KB dictionary window.

## Important APIs, Types, and Functions
The public functions are `RDG_genBuffer()` and `RDG_genOut()`. Internal helpers include `RDG_rand()` for deterministic PRNG state, `RDG_fillLiteralDistrib()` for a 8192-entry literal table, `RDG_genChar()` for weighted byte selection, and `RDG_genBlock()` for literal/match block synthesis. `litDistribTable` is a fixed `BYTE` array sized by `LTLOG`.

## Control Flow, State, and Persistence
All state is in stack buffers and the seed passed by value or pointer. `RDG_genBlock()` starts at `prefixSize`, optionally initializes the first byte, then loops until `buffSize`, choosing match copies or literal runs from PRNG output. `RDG_genOut()` first generates a 32 KB dictionary, then repeatedly fills a 128 KB block after the dictionary, writes the requested amount to stdout, and slides the trailing dictionary with `memcpy`. There is no persistent file state.

## Dependencies and Integration Points
The file depends on `platform.h` for binary stdout mode, `util.h` for fixed-width LZ4 typedefs, and libc allocation/output primitives. `datagencli.c`, benchmarks, and tests use the exported generator through `datagen.h`.

## Risks and Test Signals
Risks are unchecked `fwrite()` failures, extreme `matchProba >= 1.0` behavior producing sparse zero runs, and caller-provided buffer size assumptions. Deterministic seed behavior is a strong test signal: identical probability and seed should reproduce byte-exact output.

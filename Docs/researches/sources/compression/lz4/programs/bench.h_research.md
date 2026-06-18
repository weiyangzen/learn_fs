# sources/compression/lz4/programs/bench.h

## Purpose
`bench.h` declares the public interface from the CLI into the LZ4 benchmark engine implemented by `bench.c`.

## Important APIs, Types, And Functions
The main function is `BMK_benchFiles(const char** fileNamesTable, unsigned nbFiles, int cLevelStart, int cLevelLast, const char* dictFileName)`. Configuration setters control benchmark duration, block size, verbosity, separate-file reporting, decode-only mode, checksum skipping, and an additional hidden formatting parameter.

## Control Flow
The header has no runtime control flow. Its comments define how `BMK_benchFiles()` treats file arrays, compression level ranges, optional dictionaries, and aggregate versus separate reporting.

## State, Persistence, And Dependencies
The header includes `stddef.h` for `size_t`. Runtime state is maintained inside `bench.c` globals after callers invoke the setters. File and dictionary persistence is handled by the implementation.

## Integration Points
The LZ4 CLI includes this header to configure and invoke benchmarks. It isolates benchmark configuration from command-line parsing code.

## Risks
The API is process-global rather than context-based, so concurrent benchmark sessions cannot have independent settings. Decode-only mode and checksum skipping are version-commented but not capability-checked in the header. `BMK_setAdditionalParam()` is intentionally hidden and output-format oriented.

## Test Signals
Compile inclusion from the CLI, setter invocation before and after benchmark calls, level-range behavior, dictionary argument handling, and decode-only option combinations are the relevant signals.

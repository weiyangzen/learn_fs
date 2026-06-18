<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/dump.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/dump.h

## Purpose
`dump.h` declares native erasure-code diagnostic dump helpers.

## Important APIs, Types, and Functions
It declares `dumpEncoder()`, `dumpDecoder()`, `dump()`, `dumpMatrix()`, and `dumpCodingMatrix()`. The prototypes refer to `IsalEncoder` and `IsalDecoder` types from the erasure coder layer.

## Control Flow
There is no runtime control flow. The header only exposes diagnostic functions to implementation files.

## State and Persistence
No state is declared.

## Dependencies and Integration Points
It includes standard C headers and is expected to be used with `erasure_coder.h` in callers. It is part of the verbose debugging path for native RS coding.

## Risks and Edge Cases
The header relies on coder types being visible before or through included translation-unit ordering. If included alone before type declarations, it can fail to compile.

## Test Signals
Compile tests with warning settings and verbose erasure-code runs validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/dump.h -->

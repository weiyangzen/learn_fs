# sources/compression/zstd/lib/common/xxhash.c

## Purpose
`xxhash.c` is the xxHash implementation-instantiation unit for zstd. The real algorithm code lives in `xxhash.h`; this file defines the macros needed to emit the function bodies into one translation unit.

## Important APIs, Types, and Functions
The file defines `XXH_STATIC_LINKING_ONLY` to expose advanced declarations and `XXH_IMPLEMENTATION` to instantiate definitions, then includes `xxhash.h`. The resulting symbols are the xxHash APIs declared by the header, such as one-shot and streaming XXH32/XXH64 routines and any static-linking-only helpers enabled by the bundled header.

## Control Flow, State, and Persistence
There is no direct control flow in this file beyond preprocessing. Runtime state and behavior are entirely provided by `xxhash.h` after macro expansion, including caller-owned streaming hash states. This source file's role is to ensure those definitions are compiled once rather than as header-only duplicates.

## Dependencies and Integration Points
It depends solely on `xxhash.h`. Zstd tests and frame/block code use xxHash for checksums and verification paths, and build systems include this C file when they need standalone xxHash symbols from the bundled copy.

## Risks and Test Signals
Risks are integration-oriented: defining `XXH_IMPLEMENTATION` in multiple translation units can produce duplicate symbols, while omitting this file can produce unresolved references. Test signals include successful static and shared library links, checksum known-answer tests for XXH32/XXH64, streaming versus one-shot parity, and builds that include zstd with and without separate xxHash linkage.

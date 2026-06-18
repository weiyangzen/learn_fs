# sources/compression/zstd/programs/lorem.h

## Purpose

This header exposes the lorem-ipsum generator API for zstd tools and tests.

## Important APIs, Types, and Functions

`LOREM_genBuffer(void* buffer, size_t size, unsigned seed)` fills exactly the requested buffer size with deterministic compressible text. `LOREM_genBlock(void* buffer, size_t size, unsigned seed, int first, int fill)` adds control over whether to include the canonical first sentence and whether to fill the whole buffer or emit at most one paragraph, returning the number of bytes generated.

## Control Flow, State, and Persistence

The header declares a synchronous generation contract only. State is implementation-local in `lorem.c`, and output is written directly into the caller-provided memory.

## Dependencies and Integration Points

It includes `<stddef.h>` for `size_t` and is used by `datagen`, benchmark programs, and tests needing text-like synthetic data.

## Risks and Test Signals

Callers must provide a valid writable buffer and should not expect thread safety from the implementation. Tests should compile both C and C++ inclusions, verify return values from `LOREM_genBlock()`, and compare deterministic output across seeds and sizes.

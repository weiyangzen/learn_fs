# sources/compression/zstd/programs/lorem.c

## Purpose

This file implements a deterministic lorem-ipsum text generator used by zstd tests and benchmarks to produce printable, compressible sample data with text-like repetition.

## Important APIs, Types, and Functions

Public functions are `LOREM_genBuffer()` and `LOREM_genBlock()`. Internally it keeps a static word pool, weights by word length, a generated distribution table, and generator globals `g_ptr`, `g_nbChars`, `g_maxChars`, and `g_randRoot`. Helpers initialize the weighted distribution, produce pseudo-random numbers, write truncation-safe final characters, generate words/sentences/paragraphs, and emit the canonical first sentence.

## Control Flow, State, and Persistence

`LOREM_genBlock()` initializes output pointers and seed, lazily builds the global word distribution once, optionally writes the first sentence, then generates paragraphs until the buffer is full or one paragraph is produced in non-fill mode. If a word would overrun the requested size, `writeLastCharacters()` terminates the buffer with punctuation, spaces, and newline when possible.

## Dependencies and Integration Points

It depends only on `lorem.h`, `assert.h`, `limits.h`, and `string.h`. Test programs such as `datagen` and `fullbench` compile it for synthetic input generation.

## Risks and Test Signals

The implementation is explicitly not thread-safe because generation state is global. It asserts `size < INT_MAX` and relies on static distribution initialization without locking. Tests should verify deterministic output for fixed seeds, exact byte counts, first-sentence behavior, non-fill mode, tiny buffer boundaries, and sequential repeated calls.

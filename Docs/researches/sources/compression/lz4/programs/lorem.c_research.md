# sources/compression/lz4/programs/lorem.c

Purpose: implements LZ4's lorem ipsum generator for `datagen`, producing printable, text-like, compressible data for tests and benchmarks.

Important APIs/functions: exports `LOREM_genBlock()` and `LOREM_genBuffer()`. Internal initialization builds word lengths, a packed `g_wordBuffer`, and a weighted `g_distrib` favoring shorter words. Generation flows through `LOREM_rand()`, `generateWord()`, `generateSentence()`, `generateParagraph()`, and first/last sentence helpers.

Control flow: `LOREM_genBlock()` sets global output state, lazily initializes dictionaries/distribution, optionally emits the canonical first sentence, then writes paragraphs until the buffer is full or `fill` is false. Boundary helpers finish safely with punctuation/newlines.

State and persistence: global mutable state (`g_ptr`, counters, PRNG seed, word tables, distribution) makes this sequential-only and not thread-safe. `g_wordBuffer` is process-lifetime allocation.

Dependencies/integration: depends on `lorem.h` and C runtime headers. Built into `datagen`, which feeds many LZ4 CLI and library tests.

Risks: release builds may not enforce `assert(size < INT_MAX)`; allocation failure aborts; concurrent use races on globals; distribution capacity depends on static weights/word list.

Test signals: exercised indirectly by `datagen` in `test-lz4-*`, fuzzer, frametest, huge-file, dictionary, and memory targets.

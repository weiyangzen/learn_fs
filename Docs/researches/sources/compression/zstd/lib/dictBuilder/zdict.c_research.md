# sources/compression/zstd/lib/dictBuilder/zdict.c

## Purpose
`zdict.c` provides zstd dictionary helper APIs, dictionary finalization, entropy-table construction, the legacy suffix-array trainer, and the default `ZDICT_trainFromBuffer()` entry point. It bridges raw selected dictionary content to valid zstd dictionary format by adding magic, dictionary id, entropy tables, optional padding, and content.

## Important APIs, Types, And Functions
- `ZDICT_isError()` and `ZDICT_getErrorName()` expose zstd error handling for dictionary APIs.
- `ZDICT_getDictID()` reads a zstd dictionary id from a dictionary header.
- `ZDICT_getDictHeaderSize()` loads dictionary entropy metadata to compute header size.
- `ZDICT_finalizeDictionary()` writes a full dictionary header, computes entropy tables from samples and custom content, applies dict id policy, pads for minimum repcode offset, and copies content into final position.
- `ZDICT_addEntropyTablesFromBuffer()` and its advanced helper add entropy tables to raw content already stored at the end of the output buffer.
- `ZDICT_trainFromBuffer_legacy()` duplicates samples with a noisy guard band and runs the older suffix-array-based segment selector.
- `ZDICT_trainFromBuffer()` is the default public trainer and delegates to `ZDICT_optimizeTrainFromBuffer_fastCover()` with `d = 8`, `steps = 4`, and default compression level.
- Legacy internals include `dictItem`, `ZDICT_analyzePos()`, `ZDICT_tryMerge()`, `ZDICT_trainBuffer_legacy()`, and `ZDICT_fillNoise()`.
- Entropy internals include `ZDICT_countEStats()`, `ZDICT_analyzeEntropy()`, `ZDICT_flatLit()`, and rep-offset helpers.

## Control Flow
The default trainer initializes a FASTCOVER parameter struct and calls optimized FASTCOVER. The legacy trainer first checks minimum corpus size, copies the concatenated samples, appends deterministic noise for safe overreads in match counting, and calls `ZDICT_trainFromBuffer_unsafe_legacy()`. That path allocates a candidate segment list, builds a suffix array with `divsufsort()`, analyzes repeated substrings, merges overlapping/included `dictItem`s, limits the selected content to the target size, copies selected segments from the end of the dictionary buffer backward, then adds entropy tables.

Dictionary finalization starts by writing the magic number and a dictionary id derived from `params.dictID` or an `XXH64` hash of the custom content. It calls `ZDICT_analyzeEntropy()`, which creates a raw-content `ZSTD_CDict`, compresses each sample block, extracts literal and sequence statistics from the compressor's sequence store, normalizes FSE counts, builds a HUF table, writes entropy tables, and writes starting rep offsets. `ZDICT_finalizeDictionary()` then shrinks content if header plus content exceeds capacity, pads if content is smaller than the maximum initial repcode, and writes header, padding, and content in overlap-safe order.

## State And Persistence
All state is transient except caller-provided dictionary buffers. Legacy training owns temporary suffix, reverse suffix, done-mark, file-position, guard-band, and dict-item allocations. Entropy analysis owns a `ZSTD_CDict`, `ZSTD_CCtx`, and block workspace while collecting statistics. The output dictionary buffer persists and contains the zstd dictionary magic, id, entropy tables, padding if needed, and content.

## Dependencies And Integration Points
This file depends on zstd common memory, FSE, HUF, internal compression structures, `XXH64`, `ZSTD_loadCEntropy()`, `ZSTD_compressBlock_deprecated()`, and `divsufsort.h`. It is the central integration point for `cover.c` and `fastcover.c`, which call `ZDICT_finalizeDictionary()` for selected content. It also exposes public dictionary helper functions declared in `zdict.h`.

## Risks And Edge Cases
- Legacy match counting intentionally reads through a noisy guard band; unsafe legacy internals require callers to provide that guard.
- The legacy trainer truncates sample sets above `ZDICT_MAX_SAMPLES_SIZE` because `divsufsort()` uses int-sized indexes.
- Entropy analysis uses deprecated/internal compression APIs and sequence-store layout; compressor-internal changes can break it.
- Very noisy or too-regular literal distributions can produce non-encodable HUF tables, so `ZDICT_flatLit()` substitutes a mostly flat distribution.
- `ZDICT_finalizeDictionary()` must handle overlapping `customDictContent` and `dictBuffer`; it uses `memmove()` before writing header/padding.
- If the computed entropy header leaves too little capacity, content is shrunk; if content is below initial repcode requirements, zero padding is inserted before content.
- `ZDICT_trainFromBuffer_legacy()` returns `0` rather than an error for too-small corpora, which callers may need to distinguish from a valid empty result.

## Test Signals
Tests should validate dictionary id extraction, header-size parsing, finalization with explicit and generated dict IDs, overlap-safe finalization, too-small destination handling, tiny/insufficient corpus behavior, entropy construction on noisy and repetitive corpora, and round-trip compression/decompression using finalized dictionaries. Legacy training should be exercised with sanitizer builds, suffix-array edge cases, and corpora near size limits. Default training tests should assert that the FASTCOVER path produces a usable dictionary.

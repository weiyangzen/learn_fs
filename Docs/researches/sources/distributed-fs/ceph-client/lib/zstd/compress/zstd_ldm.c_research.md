# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm.c

## Purpose

`zstd_ldm.c` implements Zstd long distance matching. It scans input with a content-defined rolling gear hash, records candidate anchor points in a separate LDM hash table, generates `rawSeq` long-match sequences, and then integrates those sequences with normal block compression. The goal is to recover matches that are too distant or too costly for the regular per-block matchfinders to find efficiently.

## Important APIs, Types, and Functions

The public functions are `ZSTD_ldm_adjustParameters()`, `ZSTD_ldm_getTableSize()`, `ZSTD_ldm_getMaxNbSeq()`, `ZSTD_ldm_fillHashTable()`, `ZSTD_ldm_generateSequences()`, `ZSTD_ldm_skipSequences()`, `ZSTD_ldm_skipRawSeqStoreBytes()`, and `ZSTD_ldm_blockCompress()`. Internal state is built around `ldmRollingHashState_t`, which holds the current gear hash and stop mask, and around `ldmState_t`, whose table entries and bucket offsets persist across chunks.

Important helpers include `ZSTD_ldm_gear_init()`, `ZSTD_ldm_gear_reset()`, and `ZSTD_ldm_gear_feed()` for split-point discovery; `ZSTD_ldm_insertEntry()` and `ZSTD_ldm_getBucket()` for ring-bucket table maintenance; `ZSTD_ldm_countBackwardsMatch()` and `_2segments()` for extending matches backwards; `ZSTD_ldm_reduceTable()` for overflow correction; and `maybeSplitSequence()` for clipping raw sequences to a block boundary.

## Control Flow

Parameter setup starts with `ZSTD_ldm_adjustParameters()`, which derives `windowLog`, `hashRateLog`, `hashLog`, `minMatchLength`, and `bucketSizeLog` from the normal compression parameters when fields are unset. `ZSTD_ldm_fillHashTable()` can preseed the LDM table from dictionary data: it feeds bytes through the gear hash, converts split points into `xxh64()` fingerprints over `minMatchLength` bytes, and stores `offset` plus upper checksum bits in the selected bucket.

`ZSTD_ldm_generateSequences()` processes large input in 1 MiB chunks. Before each chunk it applies window overflow correction if needed, reduces stored offsets by the correction value, invalidates dictionaries on correction, and enforces max distance at the chunk end. It then delegates to `ZSTD_ldm_generateSequences_internal()`, which primes the rolling hash with `minMatchLength` bytes, batches split points into `splitIndices`, prefetches candidate buckets, and searches each bucket for checksum-compatible entries. For each candidate it measures a forward match and a backward extension, chooses the best total match, emits a `rawSeq` with literal length, match length, and offset, inserts the current entry, and advances the anchor. Overlapping/repeating patterns reset the gear hash and skip over covered bytes to avoid pathological insertion cost.

`ZSTD_ldm_blockCompress()` consumes generated sequences during normal block compression. For strategies at or above `ZSTD_btopt`, it exposes the raw sequence store through `ms->ldmSeqStore` so the optimal parser can treat LDM matches as candidates. For lower strategies, it walks the raw sequences itself, compresses literal spans with the selected block compressor, updates repcodes, stores the LDM match with `ZSTD_storeSeq()`, and finally compresses the last literal tail.

## State and Persistence Behavior

The LDM table and bucket offsets persist in `ldmState_t` across chunks and can include dictionary entries. `ZSTD_ldm_generateSequences()` updates `ldmState->window`, `loadedDictEnd`, and table offsets during overflow correction and max-distance enforcement. `RawSeqStore_t` persists generated sequences through `size`, `capacity`, `pos`, and `posInSequence`, and skip helpers mutate those fields when data is omitted or consumed. `ZSTD_ldm_blockCompress()` also mutates the normal match state tables by invoking the selected block compressor and updates `rep[]` as LDM matches are emitted.

## Dependencies and Integration Points

The file includes `zstd_ldm.h`, kernel `xxhash`, `zstd_fast.h`, `zstd_double_fast.h`, and `zstd_ldm_geartab.h`. It relies on `ZSTD_window_*` helpers, `ZSTD_count*()` match counters, `ZSTD_selectBlockCompressor()`, and `ZSTD_storeSeq()` from internal compression code. The normal fast and double-fast tables are proactively filled through `ZSTD_ldm_fillFastTables()` when LDM has skipped long spans before calling a secondary compressor.

## Risks

LDM is sensitive to offset validity over long inputs. Overflow correction must reduce table offsets consistently or stale offsets can point outside the current window. Sequence splitting is subtle because offsets must remain valid at the end of a split sequence, not only at its start. Raw sequence store capacity is a hard limit: sequence generation returns `dstSize_tooSmall` if it fills. Gear hash stop masks affect both speed and ratio, and degenerate `hashRateLog` values need bounds protection. External dictionary backward extension crosses segment boundaries and must not underflow pointers.

## Test Signals

Tests should include round trips with LDM enabled across multi-megabyte inputs, repeated-byte data, inputs with distant repeats beyond normal block windows, external dictionaries, and dictionary preloading. Error tests should force small raw sequence capacity. Streaming tests should skip bytes with both `ZSTD_ldm_skipSequences()` and `ZSTD_ldm_skipRawSeqStoreBytes()`, split sequences across block boundaries, and exercise overflow correction by feeding high logical offsets. Strategy coverage should include fast/dfast direct LDM consumption and btopt/btultra candidate integration.

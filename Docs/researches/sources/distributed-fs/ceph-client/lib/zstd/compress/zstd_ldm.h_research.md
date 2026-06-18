# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm.h

## Purpose

`zstd_ldm.h` declares the internal long-distance matching interface. It exposes the functions needed to size LDM workspaces, adjust LDM parameters, prefill long-match hash tables, generate raw long-match sequences, skip unused sequence ranges, and combine LDM sequences with normal block compression.

## Important APIs, Types, and Functions

`ZSTD_LDM_DEFAULT_WINDOW_LOG` maps the LDM default window to `ZSTD_WINDOWLOG_LIMIT_DEFAULT`. `ZSTD_ldm_fillHashTable()` seeds an `ldmState_t` table from `[ip, iend)`. `ZSTD_ldm_generateSequences()` populates a `RawSeqStore_t` with long-range matches for a source range. `ZSTD_ldm_blockCompress()` consumes those predefined sequences while running a selected secondary compressor. `ZSTD_ldm_skipSequences()` and `ZSTD_ldm_skipRawSeqStoreBytes()` advance sequence-store cursors for data that will not be compressed through the LDM path. `ZSTD_ldm_getTableSize()` and `ZSTD_ldm_getMaxNbSeq()` are workspace sizing helpers. `ZSTD_ldm_adjustParameters()` derives unset LDM parameters from normal compression parameters.

## Control Flow

Callers normally adjust parameters, allocate table and raw sequence capacity from the sizing helpers, update the LDM window for the incoming source, generate sequences, then either call `ZSTD_ldm_blockCompress()` for each block or skip the corresponding sequence bytes when data is handled elsewhere. The header documents that `ZSTD_window_update()` must be called for all available input before `ZSTD_ldm_generateSequences()` and that the generated sequence store must have enough capacity.

## State and Persistence Behavior

The declared API mutates `ldmState_t`, `RawSeqStore_t`, `ZSTD_MatchState_t`, `SeqStore_t`, and `rep[]`, but the header itself stores no state. `RawSeqStore_t::pos` and `posInSequence` are explicitly part of the consumption protocol. `ZSTD_ldm_blockCompress()` may split a raw sequence between blocks and update the store accordingly.

## Dependencies and Integration Points

The header includes `zstd_compress_internal.h` for internal compression types such as `ldmParams_t`, `ldmState_t`, `RawSeqStore_t`, `SeqStore_t`, and `ZSTD_MatchState_t`, plus `<linux/zstd.h>` for public context types and `size_t`. It is used by the compressor context setup and by `zstd_ldm.c`. Optimal parsing integrates with the same raw sequence store through `ms->ldmSeqStore`.

## Risks

The most important contract risk is cursor misuse: `ZSTD_ldm_skipSequences()` and `ZSTD_ldm_skipRawSeqStoreBytes()` are documented as not interchangeable. Mixing them can desynchronize `pos` and `posInSequence`. The header comment also states that `ZSTD_ldm_blockCompress()` does not return errors, while `ZSTD_ldm_generateSequences()` can; callers must handle generation errors before compression. The closing include guard comment says `ZSTD_FAST_H`, which is harmless but misleading.

## Test Signals

Interface tests should validate table size is zero when LDM is disabled, max sequence estimates are nonzero only when enabled, generated sequences can be consumed block by block, and skipped input leaves the raw store cursor at the expected sequence and in-sequence position. Build tests should catch signature drift with `zstd_ldm.c`.

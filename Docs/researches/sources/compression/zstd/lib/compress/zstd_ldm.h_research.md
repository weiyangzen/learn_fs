# sources/compression/zstd/lib/compress/zstd_ldm.h

## Purpose
`zstd_ldm.h` declares the long-distance matching interface used by the compressor context, block-compressor pipeline, and parameter initialization code.

## Important APIs, Types, And Functions
The header defines `ZSTD_LDM_DEFAULT_WINDOW_LOG` and declares table initialization, sequence generation, raw-sequence skipping, block compression with predefined LDM sequences, memory sizing, maximum sequence estimation, and parameter adjustment APIs. The key data types are imported from internal headers: `ldmState_t`, `ldmParams_t`, `RawSeqStore_t`, `ZSTD_MatchState_t`, `SeqStore_t`, and `ZSTD_ParamSwitch_e`.

## Control Flow
There is no direct runtime flow. The documented contract requires callers to update the LDM window before sequence generation, allocate enough raw-sequence space, call skip helpers for data not passed to `ZSTD_ldm_blockCompress()`, and adjust parameters before sizing or running LDM.

## State And Persistence
The header owns no storage. It describes operations over LDM hash state, raw sequence stores, normal match state, and repcode arrays. Generated raw sequences persist in memory until consumed or skipped.

## Dependencies And Integration Points
It includes `zstd_compress_internal.h` and public `zstd.h`. It is included by `zstd_ldm.c` and by compression-context code that sizes LDM tables, fills dictionary tables, generates sequences, or routes blocks through LDM-aware compression.

## Risks
The API has strict ordering requirements: stale windows or insufficient raw sequence capacity produce invalid offsets or errors. `ZSTD_ldm_blockCompress()` accepts sequences longer than a block and mutates the raw sequence store, so callers must not assume one sequence maps to one block.

## Test Signals
Header-level signals are successful compilation across LDM-enabled and disabled parameter paths, plus integration tests that verify adjusted defaults, memory sizing, and raw-sequence consumption over multiple blocks.

# sources/compression/zstd/lib/dictBuilder/cover.h

## Purpose
`cover.h` is the internal interface shared by zstd's COVER and FASTCOVER dictionary builders. It defines candidate-selection state, segment and epoch helper types, dictionary-selection result ownership, and the utility functions needed by `cover.c` and `fastcover.c`.

## Important APIs, Types, And Functions
- `COVER_best_t` combines a mutex, condition variable, live job count, best dictionary pointer/size, winning `ZDICT_cover_params_t`, and best compressed-size score.
- `COVER_segment_t` describes a chosen source range with `begin`, `end`, and `score`.
- `COVER_epoch_info_t` records the number and size of epochs used for segment selection.
- `COVER_dictSelection_t` owns a finalized candidate dictionary and its total compressed-size score.
- `COVER_computeEpochs()`, `COVER_warnOnSmallCorpus()`, and `COVER_sum()` are shared corpus/epoch helpers.
- `COVER_checkTotalCompressedSize()` evaluates a dictionary against sample ranges.
- `COVER_best_init/wait/destroy/start/finish()` provide a small synchronization and best-result API.
- `COVER_selectDict()` finalizes raw dictionary content and optionally performs shrink-dictionary selection.

## Control Flow
The header is included after forcing `ZDICT_STATIC_LINKING_ONLY`, so it may expose and consume zstd experimental/static dictionary-training structures. A typical optimized training path initializes `COVER_best_t`, starts jobs before dispatch, lets each job call `COVER_selectDict()`, reports its `COVER_dictSelection_t` through `COVER_best_finish()`, waits for all jobs, then destroys the best-state object.

## State And Persistence
The header defines ownership expectations rather than storing state itself. `COVER_best_t` owns the copied winning dictionary after successful `finish()` calls. `COVER_dictSelection_t` owns `dictContent` until it is transferred/copied or released by `COVER_dictSelectionFree()`. All APIs are process-local; no persistent storage is involved.

## Dependencies And Integration Points
It depends on zstd pthread wrappers from `common/threading.h`, zstd integer and byte types from `common/mem.h`, and `../zdict.h` for parameter types. `fastcover.c` relies on this header heavily to avoid duplicating dictionary finalization, scoring, and threaded best-candidate coordination. Consumers must compile with compatible zstd static-linking-only definitions.

## Risks And Edge Cases
- The thread-safety guarantee is conditional on zstd being built with multithread support; otherwise wrapper behavior depends on the configured threading backend.
- `COVER_best_init()` is the only method documented as not requiring prior initialization. Other methods assume a valid initialized object unless they explicitly return on `NULL`.
- `COVER_dictSelectionIsError()` treats a missing dictionary pointer as an error, even if the score is not an error code.
- The contract for `offsets`, train/check sample counts, and dictionary buffer capacity is shared implicitly with implementation files, so mismatched callers can score the wrong sample range.

## Test Signals
Tests should exercise `COVER_best_t` under serial and threaded candidate completion, verify dictionary-selection ownership/freeing, validate `COVER_computeEpochs()` around small corpora and large dictionaries, and compare `COVER_checkTotalCompressedSize()` against direct compression with a known `ZSTD_CDict`.

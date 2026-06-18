# sources/distributed-fs/eos/mgm/tgc/SmartSpaceStats.cc

## Purpose
`SmartSpaceStats.cc` implements per-space stats smoothing for tape-GC. It periodically queries MGM space stats, optionally overrides available bytes with an external script, adjusts the freed-byte histogram to match query period, and adds recently queued-for-deletion bytes to reported available space.

## Important APIs, Types, And Functions
Implemented methods include constructor, `get()`, `getQueryTimestamp()`, and `diskReplicaQueuedForDeletion()`. The core collaborators are `CachedValue<SpaceConfig>`, `AsyncUint64ShellCmd`, `FreedBytesHistogram`, `ITapeGcMgm`, and `CtaUtils`.

## Control Flow
`get()` reads cached config, locks, and refreshes MGM stats when the query period has elapsed. It always calls `m_mgm.getSpaceStats()`, then either keeps internal avail bytes, polls `tgc.freebytesscript`, uses a just-finished script value, uses a previous script value while pending, or logs script errors and falls back. It validates query period, recalculates histogram bin width as `ceil(queryPeriodSecs / nbBins)`, and adds freed bytes from the last query period to `availBytes`.

## State And Persistence
State is in memory: last query timestamp, last MGM stats plus source enum, real clock, freed-byte histogram, async script runner, and config cache reference. There is no durable persistence.

## Dependencies And Integration Points
`TapeGc` uses this class to decide whether eviction is needed and to report stats. `RealTapeGcMgm` supplies production stats/script execution; `DummyTapeGcMgm` supports tests. Config keys come from `Constants.hh`.

## Risks And Edge Cases
The `PENDING_AND_PREVIOUS_VALUE` switch case lacks a `break`, so it falls through to `VALUE`; because `getValue()` is absent, it keeps the previous value, but this fallthrough should be explicit or fixed for clarity. If `getSpaceStats()` throws, the method logs and continues with default/previous state. Invalid query periods are logged but still used later for freed-byte query depth. Adding freed bytes can double-count until MGM stats catch up, as the comment acknowledges.

## Test Signals
Existing `SmartSpaceStatsTests` cover no-script and script paths. Additional tests should cover query-period caching, invalid query periods, script error fallback, previous-value pending behavior, histogram bin-width changes, freed-byte augmentation, `TooFarBackInTime` fallback, and exception paths from `getSpaceStats()`.

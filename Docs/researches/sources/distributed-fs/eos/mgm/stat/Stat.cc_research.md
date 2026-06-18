# sources/distributed-fs/eos/mgm/stat/Stat.cc

## Purpose
`Stat.cc` implements the MGM statistics accumulator declared in `Stat.hh`. It records per-command counters keyed by UID, GID, and optional FUSE application, tracks rolling request rates and extended sample/min/max aggregates, stores recent execution timings, prints table or monitoring output, and runs a circulation thread that advances circular buckets and optionally samples instrumented namespace/FsView/quota lock timing.

## Important APIs, Types, And Functions
Important methods include `Stat::Add()`, `AddExt()`, `AddExec()`, `GetTotal*()`, `GetExec()`, `GetTotalExec()`, `GetReadContention()`, `GetWriteContention()`, `Clear()`, `PrintOutTotal()`, and `Circulate()`. The implementation relies on `StatAvg` and `StatExt` bucket methods from the header, `TableFormatterBase` for presentation, `common::Statistics` for average/sigma/percentile calculations, and `common::Mapping` for UID/GID name translation.

## Control Flow
`Add()` and `AddExt()` take `mMutex` and update total, rolling-average, or extended maps. Execution timing samples are appended to a per-tag deque and capped at 100 samples. Getter methods assume their caller already holds the mutex except for contention helpers, which lock internally and query global `gOFS->MgmStats`. `PrintOutTotal()` locks, snapshots tags, builds an all-users table, optionally unlocks to translate UID/GID names, relocks, collects user/group/app rows, sorts them, and appends generated tables. `Circulate()` sleeps about 512 ms, optionally samples instrumented mutex counters, then stamps the next bucket of each rolling structure to zero.

## State And Persistence
All state is in memory under `Stat::mMutex`; there is no durable persistence. The class stores sparse maps by tag and identity, execution deques, and cumulative execution time. The circulation thread mutates bucket arrays to age out old samples, so values are time-window approximations rather than audit logs.

## Dependencies And Integration Points
The file integrates with MGM global `gOFS`, `FsView::gFsView`, quota locks, namespace locks, EOS table formatting, UID/GID mapping, and command timing macros in `Stat.hh`. Admin/monitoring code can call `PrintOutTotal()` to expose totals, rates, execution timings, and contention estimates.

## Risks And Edge Cases
Most getters are documented as requiring external locking; accidental unlocked use risks races. Extended weighted-average methods divide by total sample weight without guarding `totw == 0` when a tag exists but has no samples. `Clear()` iterates `StatsUid` and clears associated maps but does not explicitly iterate tags that exist only in extended maps. `Circulate()` stamps `StatExtGid` twice and does not stamp `StatExtUid`, which looks like a copy/paste bug affecting rolling extended UID windows. Manual `mMutex.Lock()`/`UnLock()` in `PrintOutTotal()` makes exception safety more fragile than RAII.

## Test Signals
Useful tests include rate-window aging, extended min/max/average aggregation with empty and non-empty sample sets, execution timing percentile output, monitoring and human table modes, app-only output, UID/GID translation while stats mutate, `Clear()` behavior for all maps, contention reporting under `EOS_INSTRUMENTED_RWMUTEX`, and sanitizer/TSAN coverage of concurrent `Add()` plus `PrintOutTotal()`.

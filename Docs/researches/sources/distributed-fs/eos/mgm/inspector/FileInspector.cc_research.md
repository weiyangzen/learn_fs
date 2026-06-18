# sources/distributed-fs/eos/mgm/inspector/FileInspector.cc

## Purpose

`FileInspector.cc` implements a background MGM service that periodically scans QuarkDB file metadata for a storage space, computes file-health, age, size, cost, usage, and link statistics, persists the last scan into QuarkDB, and renders current/last scan data for admin and monitoring commands.

## Important APIs, Types, and Functions

- `FileInspector::FileInspector(std::string_view, const QdbContactDetails&)` initializes root identity, starts an assisted background thread, sets default disk/tape prices, and prepares the QuarkDB stats helper.
- `~FileInspector()` joins the assisted thread.
- `getOptions(LockFsView)` reads `inspector`, `inspector.interval`, `inspector.price.disk.tbyear`, `inspector.price.tape.tbyear`, and `inspector.price.currency` from `FsView::gFsView` for the configured space.
- `backgroundThread(ThreadAssistant&)` waits for namespace boot, loads previous stats from QuarkDB, periodically checks options, and runs scans only when enabled and the local MGM is master.
- `performCycleQDB(ThreadAssistant&)` scans all QuarkDB file metadata with `FileScanner`, throttles scan speed to fit the configured interval, handles disable/mastership changes, stores completed stats, and resets current stats.
- `Process(std::shared_ptr<IFileMD>)` updates `mCurrentStats` for one file: symlink/hardlink counters, totals, zero-size/nolocation/shadow-location/repetition-delta classifications, access-time bins, birth-time bins, birth-vs-access bins, size bins, birth-vs-size bins, disk/tape cost, and disk/tape byte attribution by uid/gid.
- `Dump(std::string&, std::string_view, LockFsView)` renders state for human output, export/list modes, and monitoring `key=...` lines.
- `QdbHelper::Store()` and `QdbHelper::Load()` marshal/unmarshal selected `FileInspectorStats` fields into a QuarkDB hash named `eos-file-inspector-stats`.

## Control Flow

The constructor starts `backgroundThread`. That thread waits for namespace boot via `gOFS->WaitUntilNamespaceIsBooted()`, reads the initial space options under the fs-view lock, sleeps briefly, loads last stats from QuarkDB if present, then loops until termination. Each loop refreshes options, enables or disables the inspector atomic, starts an interval stopwatch, runs `performCycleQDB()` only if enabled and `gOFS->mMaster->IsMaster()` is true, then sleeps for the remainder of the configured interval.

`performCycleQDB()` lazily creates a `qclient::QClient`, reads namespace file/container counts under `gOFS->eosViewRWMutex`, creates a `FileScanner`, and iterates through QuarkDB file metadata. Each protobuf item is wrapped in a `QuarkFileMD` and sent to `Process()`. The method updates `scanned_percent` and may sleep up to five seconds at a time to pace the scan across the configured interval. Once per minute it refreshes options and mastership; either disablement or loss of mastership interrupts the scan. Scanner errors are logged and break the loop. At the end it sets progress to 100%, moves `mCurrentStats` to `mLastStats`, persists `mLastStats`, and resets `mCurrentStats`.

`Process()` holds `mutexScanStats` for the entire per-file update. Symlinks and hardlinks are counted and returned early. Normal files update layout-keyed scan stats and global totals. It records faults for missing locations, shadow filesystem locations, shadow deletion locations, and replication deltas up to `maxfaulty` examples while still incrementing total fault count. Time histograms use a fixed bin set ranging from 0 through one day, seven days, month-scale/year-scale values, and an undefined bin. Cost and byte accounting are split into disk index 0 and tape index 1.

`Dump()` first emits human summary and a size histogram unless monitoring mode is requested. It then rejects disabled state. With lock held, monitoring mode emits line-oriented `key=last` metrics. Non-monitoring mode reports progress and optionally current scan data (`c`), last scan data (`l`), printed faulty files (`p`), exported faulty file lists (`e`), and filtered sections for layouts/costs/usage/access/birth/birth-vs-access. `Z` expands top-N listings, and `M` switches cost display from TB-years to configured currency.

## State and Persistence Behavior

Live state includes `mEnabled`, `mCurrentStats`, `mLastStats`, pricing atomics, currency string, scan progress, namespace file/directory counters, `mQcl`, and `mSpaceName`. `mutexScanStats` protects current/last stats during processing and dumps. The background thread lifecycle is managed by `AssistedThread`.

Persistent state is a QuarkDB hash at key `eos-file-inspector-stats` through `QdbHelper`. Store/load cover scan stats, faulty files, access/birth/birth-vs-access distributions, user/group/total costs, user/group/total bytes, faulty count, scan time, and link counts. The code computes size distributions and birth-vs-size distributions, but `QdbHelper::Store()` and `Load()` do not persist `SizeBinsFiles`, `SizeBinsVolume`, `BirthVsSizeFiles`, `BirthVsSizeVolume`, `TotalFileCount`, or `TotalLogicalBytes` despite `Dump()` using them for last-scan summary and monitoring output.

## Dependencies and Integration Points

The implementation depends on global MGM state (`gOFS`), master-state interface (`gOFS->mMaster`), filesystem view (`FsView::gFsView`), namespace services, QuarkDB contact details and qclient, `FileScanner`, `QuarkFileMD`, EOS layout metadata helpers, EOS timing/string conversion helpers, EOS user/group mapping, and `ProcCommand`/MGM admin command integration through `Dump()` output.

The inspector is space-specific and reads its runtime configuration from the corresponding space view. It is master-only to avoid multiple MGMs scanning and writing overlapping stats.

## Risks and Edge Cases

- `mCurrentStats.TimeScan` is set before `performCycleQDB()` in the background thread, but a direct caller of `performCycleQDB()` could run with a zero scan time and skew age bins.
- If `nfiles` is zero, progress and pacing calculations divide by `nfiles`.
- `QdbHelper::Store()` does not persist fields that `Dump()` later presents as last-scan data, especially total file/byte summary and size/birth-vs-size histograms.
- `FileInspectorStats` defines `SIZE_*` keys, but this implementation does not store/load those keys.
- Currency parsing accepts indexes `< 6` but does not reject negative values before indexing the six-element array, so a negative parsed index can access out of bounds.
- Cost maps are `uint64_t` in `FileInspectorStats`, but `Process()` accumulates `double` costs into them, truncating fractional values.
- Faulty examples are capped by a global `NumFaultyFiles` count across all categories, so some categories may have no examples once the cap is reached.
- `Dump()` builds very large strings under the stats mutex, which can block scanning on large outputs.
- Export mode writes to `/var/log/eos/mgm/FileInspector.<time>.list`; failures are reported in output but not otherwise recoverable.
- `QdbHelper::Load()` catches all unmarshal errors and resets all stats, which is robust but can hide partial schema migration issues.

## Test Signals

Tests should cover option parsing with/without fs-view locking, master-only scan gating, scan interruption when disabled or demoted, zero-file namespaces, symlink/hardlink early returns, missing/shadow/repetition-delta fault classification, age and size bin boundaries, disk/tape cost and bytes attribution, QDB store/load round trips for every field used by `Dump()`, monitoring output shape, export/list modes, and negative/invalid currency or price config values.

# sources/distributed-fs/eos/mgm/inspector/FileInspector.hh

## Purpose

`FileInspector.hh` declares the space-scoped file-inspection service used by MGM to scan QuarkDB file metadata and report storage health/cost/usage statistics. It defines the public control/reporting surface, the background thread state, and the nested QuarkDB persistence helper.

## Important APIs, Types, and Functions

- `struct Options` contains `enabled` and scan `interval`.
- `enum LockFsView` lets callers decide whether `getOptions()`/`Dump()` should lock the global fs-view mutex.
- `FileInspector(std::string_view, const QdbContactDetails&)` and `~FileInspector()` manage the inspector lifecycle.
- `performCycleQDB(ThreadAssistant&) noexcept` exposes one QDB scan cycle.
- `Dump(std::string&, std::string_view, LockFsView)` renders current/last stats.
- `getOptions(LockFsView)` reads space configuration and updates enabled/pricing state.
- `enabled()`, `disable()`, and `enable()` wrap atomic inspector state transitions.
- Private `backgroundThread()` and `Process()` implement periodic scanning and per-file accounting.
- Nested `QdbHelper` owns a qclient and `QHash`, and provides `Store()`, `Load()`, `Clear()`, and `HasStats()`.

## Control Flow

The header describes a service where construction starts the assisted background thread. The thread periodically calls `getOptions()`, uses mastership checks in the implementation, and invokes `performCycleQDB()` to populate stats. Admin/monitoring callers use `Dump()` to view either current scan progress or last completed scan output.

`enable()` and `disable()` are compare-exchange operations, so they return true only when they actually change the current enabled state. `enabled()` returns the current atomic value.

## State and Persistence Behavior

Important in-memory state includes:

- `AssistedThread mThread` for the background scanner.
- `std::atomic<bool> mEnabled`.
- `mVid` root identity and `mError` error object.
- `mQcl` for scanner access to QuarkDB.
- `mCurrentStats` and `mLastStats`.
- Atomic disk/tape prices, currency string, scanned percentage, file/dir counters.
- `mutexScanStats` guarding stats.
- `mSpaceName`.

Persistent behavior is encapsulated in `QdbHelper`, which stores stats under `kFileInspectorStatsKey = "eos-file-inspector-stats"` via a QuarkDB hash. `Clear()` deletes that key, and `HasStats()` tests for it.

## Dependencies and Integration Points

The header depends on `VirtualIdentity`, `AssistedThread`, `FileInspectorStats`, QuarkDB contact details, qclient, QHash, `IFileMD`, and XRootD error types. It is intended for MGM components that already have global namespace and fs-view context.

The `LockFsView` argument is an integration affordance: some callers already hold the fs-view lock and must avoid taking it again, while others need safe option reads.

## Risks and Edge Cases

- `currency` is a plain string, not atomic and not separately guarded in the header; implementation writes it while dumps may read it.
- `currencies` is a fixed public const array, while config parsing uses numeric indexes rather than symbolic names.
- `performCycleQDB()` is public, but its implementation relies on global MGM state and background-thread initialization conventions.
- `QdbHelper` uses a single fixed QuarkDB key. If multiple spaces instantiate inspectors against the same QDB, stats may collide unless higher-level deployment guarantees only one relevant space or key namespace.
- The header exposes `disable()`/`enable()` as state toggles, but actual options are also refreshed from fs-view config, so manual toggles may be overwritten.

## Test Signals

Tests should instantiate with fake QDB contact details or a mock qclient layer, verify atomic enable/disable return semantics, exercise `getOptions()` with lock on/off, confirm `QdbHelper::Clear()`/`HasStats()` behavior, and ensure multiple space names do not unintentionally share persistent state if the service is expected to be per-space.

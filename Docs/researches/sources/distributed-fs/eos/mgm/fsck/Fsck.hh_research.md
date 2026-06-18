<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/Fsck.hh -->
# sources/distributed-fs/eos/mgm/fsck/Fsck.hh

## Purpose

`Fsck.hh` declares the MGM filesystem-check engine. It defines the public control, reporting, collection, and repair API used by admin commands and by `FsckEntry` repair outcomes.

## Important APIs, Types, and Functions

Public APIs include constructor/destructor, `Stop()`, `PrintOut()`, `Config()`, `Report()`, `PublishLogs()`, `Log()`, `LogMonitor()`, `ApplyConfig()`, `StoreConfig()`, `CollectErrs()`, `RepairErrs()`, `RepairEntry()`, `NotifyFixedErr()`, `SetMaxThreadPoolSize()`, `GetThreadPoolInfo()`, and `ForceCleanQdbOrphans()`. The private `ErrMapT` maps error-name to file-id to filesystem-id set. Configuration keys and flags track collection, repair, best-effort mode, repair category, and interval.

## Control Flow

The declaration separates collector, repair submitter, and individual repair entry logic. The collector populates `eFsMap`; the repair thread processes entries and delegates file-specific decisions to `FsckEntry`; fixed notifications flow back through `NotifyFixedErr()` to update QuarkDB.

## State and Persistence Behavior

State includes atomics for display and thread flags, repair category, in-memory logs, collection interval, guarded error maps, unavailable/dark filesystem counters, timestamp, queue/thread-pool limits, assisted threads, thread pool, and QuarkDB client. Persistent effects are stored through config engine and QuarkDB, not directly by the header.

## Dependencies and Integration Points

The header depends on `FsckEntry`, common filesystem/file-id/thread-pool helpers, MGM id tracker, namespace file metadata interfaces, and QuarkDB qclient. It is integrated with `FsView`, global MGM services, and EOS admin/reporting commands.

## Risks and Edge Cases

Several public methods are thread entry points and must tolerate asynchronous shutdown. Many members are atomic, but map/log access still requires the declared mutexes. The public `Log()` APIs are `printf`-style and can be misused by callers. `RepairEntry()` accepts arbitrary error strings and filesystem sets, so validation must be strong in implementation.

## Test Signals

Tests should verify object lifecycle start/stop, thread-pool sizing, config persistence, report API combinations, `NotifyFixedErr()` batching, and category-specific repair dispatch using fake `FsckEntry` or mocked backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/Fsck.hh -->

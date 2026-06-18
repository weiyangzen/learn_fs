<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/kvstore/mapstore.go -->
# sources/distributed-fs/beegfs-go/common/kvstore/mapstore.go

Purpose: generic, BadgerDB-backed, thread-safe key/value store with per-entry locks, optional auto-generated ordered primary keys, lexicographic iteration, delete/update commit options, and background value-log garbage collection.

Important APIs/types/functions: `EntryLock`, `badgerEntry[T]`, `BadgerItem[T]`, `MapStore[T]`, options `WithPKBandwidth`, `WithPKWidth`, `WithPKBase`, constructor `NewMapStore`, entry APIs `GenerateNextPK`, `CreateAndLockEntry`, `GetAndLockEntry`, `GetEntry`, `DeleteEntry`, `GetEntries`, commit options `WithDeleteEntry`, `WithUpdateOnly`, `WithHoldLockOnFailure`, and garbage-collection types/functions `badgerGarbageCollection`, `NewBadgerGarbageCollection`, GC option setters, `StartRunner`, `runner`, `attemptGarbageCollection`, `runGarbageCollection`, `getSleepInterval`, and `systemLoad.isSystemLoadHigh`.

Control flow: `NewMapStore` opens Badger, creates a reserved sequence, starts GC, and returns a close function that releases the sequence and closes DB. Entry creation/get obtains a per-key `EntryLock`, loads or initializes a gob-encoded `badgerEntry`, and returns a commit closure. Commit closures update, delete, optionally keep the lock for further updates, or hold the lock on failure. `GetEntries` creates a read transaction/iterator, seeks by prefix/start key, skips reserved internal keys, optionally stops at `stopKey`, decodes values, advances after each item, and provides cleanup. GC runs in a single goroutine, sleeps with jitter, defers when normalized load is high, forces after a threshold, and loops `RunValueLogGC` until no rewrite or load rises.

State and persistence: persistent state is Badger key/value data plus Badger's internal reserved sequence key. Values are gob-encoded `badgerEntry[T]`. In-memory state includes the `entryLocks` map, sequence object, config, and GC runner context/channel.

Dependencies and integration points: depends on `badger/v4`, `encoding/gob`, `types.MultiError`, `/proc/loadavg`, `runtime.NumCPU`, and `testify/mock` for test mocks in the production file. `filesystem/walk_test.go` uses `MapStore` to compare Badger lexicographic ordering with filesystem walking.

Risks: `WithPKBase` assigns `cfg.pkSeqWidth = base` instead of `cfg.pkSeqBase`, likely a bug. `WithValue` type asserts `cfg.value.(T)` and panics on wrong type. `DeleteEntry` may call `deleteEntry` with a nil lock if `getEntryLock` returns an unexpected error other than `ErrEntryAlreadyDeleted`. `GetEntries` cleanup can be called multiple times even after automatic cleanup; Badger iterator/txn double-close behavior should be verified. GC option `WithSystemLoadThreshold` replaces `systemLoad` without preserving `readFile`, but production default still uses `os.ReadFile`.

Test signals: mapstore tests are not in this item, but `mapstore.go` includes mock GC/load types and a testing constructor, and other files in the repository reference extensive tests/benchmarks. This subset directly sees integration through `filesystem/walk_test.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/kvstore/mapstore.go -->

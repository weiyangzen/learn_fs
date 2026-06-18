# sources/distributed-fs/juicefs/pkg/meta/tkv_badger.go

## Purpose
`tkv_badger.go` adapts BadgerDB v4 into the generic transactional KV metadata interface, enabled when the `nobadger` build tag is absent. It provides an embedded local metadata backend.

## Important APIs, Types, and Functions
The key types are `badgerTxn` and `badgerClient`. `badgerTxn` implements `id`, `get`, `gets`, `scan`, `exist`, `set`, `append`, `incrBy`, and `delete`. `badgerClient` implements `tkvClient` with `txn`, `simpleTxn`, `scan`, `reset`, `close`, `gc`, `shouldRetry`, `rewind`, and `name`. `newBadgerClient` opens the database and registers `drivers["badger"]`.

## Control Flow and State
Each transaction creates a writable Badger transaction, runs the caller closure, converts recovered Badger errors into returned errors, and commits unless the closure failed. `scan` can optimize prefix scans when `end == nextKey(begin)` and suppress value prefetch for keys-only scans. Top-level `scan` uses a read transaction and a prefetched iterator. `reset(nil)` drops all data; prefix reset calls `DropPrefix`.

## State and Persistence Behavior
Badger stores the full metadata keyspace on local disk at the configured path. Transaction ids combine Badger read timestamp and a local atomic sequence so changelog keys are less likely to collide. A background hourly ticker repeatedly runs Badger value-log GC at discard ratio 0.7 until no more work is available. `close` stops the ticker and closes the DB.

## Dependencies and Integration Points
It depends on `github.com/dgraph-io/badger/v4` and JuiceFS logger utilities. It plugs into `newKVMeta("badger", ...)`, `tkv.go` transaction retry handling, dump/load, and the shared backend test suite.

## Risks and Test Signals
Risks include large transaction failures such as `badger.ErrTxnTooBig`, iterator lifetime mistakes, value-log GC goroutine leaks if `close` is skipped, and prefix/drop behavior deleting too much if prefixes are wrong. Tests cover `TestBadgerClient`, `TestBadgerKV`, keys-only scan nil values, and a too-large delete transaction returning `ErrTxnTooBig`.

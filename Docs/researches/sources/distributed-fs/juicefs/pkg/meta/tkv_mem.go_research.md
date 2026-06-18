# sources/distributed-fs/juicefs/pkg/meta/tkv_mem.go

## Purpose
`tkv_mem.go` implements the in-memory `memkv` transactional KV backend used for tests and lightweight local runs.

## Important APIs, Types, and Functions
Types are `memTxn`, `kvItem`, and `memKV`. It registers `memkv` in `init`. `nextKey` is defined here and shared by other KV backends. `newMockClient` loads a persisted `setting` snapshot from `/tmp/juicefs.memkv.setting.json`.

## Control Flow and State
`memTxn` buffers writes and records observed versions during reads/scans/existence checks. Commit locks the B-tree, validates observed versions for optimistic concurrency, optionally persists the transaction buffer when it contains `setting`, then applies buffered puts/deletes. Scans operate over a locked store for transaction scans and over a cloned B-tree snapshot for client-level scans.

## State and Persistence Behavior
Most data is process-local in a Google B-tree. Only a transaction buffer containing the `setting` key is JSON-written to `settingPath`, allowing basic format persistence between mock-client creations. Transaction ids are monotonic local integers. `reset(nil)` replaces the B-tree; prefix reset scans and deletes matching keys transactionally.

## Dependencies and Integration Points
It depends on `github.com/google/btree`, JSON, and the generic KV metadata interfaces. It is the default raw test backend for `testTKV` and the full metadata `TestMemKVClient`.

## Risks and Test Signals
Risks include returning internal value slices without copying, coarse locking, limited persistence semantics, `nextKey` panic on all-0xFF prefixes, and optimistic conflict behavior diverging from real backends. Tests exercise full metadata behavior and generic scans, gets, counters, zero-byte keys, and large scans.

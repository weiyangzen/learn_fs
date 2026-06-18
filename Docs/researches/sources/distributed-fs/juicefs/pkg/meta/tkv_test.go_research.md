# sources/distributed-fs/juicefs/pkg/meta/tkv_test.go

## Purpose
`tkv_test.go` provides shared test coverage for transactional KV clients and selected backend integrations.

## Important APIs, Types, and Functions
Backend tests include `TestMemKVClient`, `TestTiKVClient`, `TestBadgerClient`, `TestEtcdClient`, `TestBadgerKV`, `TestEtcd`, and `TestMemKV`. `testTKV` is the reusable raw-client contract test. Badger-specific regression tests are `TestBadgerScanKeysOnlyNilValues` and `TestBadgerDeleteTxnTooBig`.

## Control Flow and State
`testTKV` resets the backend, verifies empty existence, set/append/get/gets, client and transaction scans over ranges/prefixes, deletes, counter increments including negative values, keys containing zero bytes, and large ordered scans over 100,000 generated key/value pairs. Full metadata tests create `kvMeta` engines and delegate to package-level `testMeta`.

## State and Persistence Behavior
Tests mutate real backends and usually isolate data via temp dirs, prefixes, or configured external endpoints. Badger tests use temporary directories except one legacy `test_badger` path. Etcd and TiKV tests depend on external services and have skip comments/environment guards.

## Dependencies and Integration Points
The file ties all KV adapters to the shared metadata test suite. It depends on Badger for direct regression setup and on environment variables such as `ETCD_ADDR` and `SKIP_NON_CORE`.

## Risks and Test Signals
Passing `testTKV` signals backend compliance for ordering, prefix scans, nil values, append, delete, counters, and high-volume iteration. Gaps include transaction conflict simulation, changelog semantics, crash recovery, and large real metadata operations beyond what `testMeta` covers.

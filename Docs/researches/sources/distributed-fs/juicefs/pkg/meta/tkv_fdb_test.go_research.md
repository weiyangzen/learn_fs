# sources/distributed-fs/juicefs/pkg/meta/tkv_fdb_test.go

## Purpose
`tkv_fdb_test.go` contains FoundationDB-specific integration tests behind the `fdb` build tag.

## Important APIs, Types, and Functions
`TestFdbClient` creates a full metadata engine with `newKVMeta("fdb", "/etc/foundationdb/fdb.cluster?prefix=test2", testConfig())` and runs `testMeta`. `TestFdb` creates a raw FDB transactional KV client with prefix `test1` and runs shared `testTKV`.

## Control Flow and State
Both tests require a FoundationDB cluster file at `/etc/foundationdb/fdb.cluster`. The tests use separate prefixes to avoid colliding engine-level and raw-KV coverage. The file uses comments indicating mutate-test skipping and disables unchecked error linting.

## State and Persistence Behavior
The tests write real FoundationDB state and rely on `testTKV` resetting its backend. `testMeta` exercises complete JuiceFS metadata behavior over persistent FDB keys.

## Dependencies and Integration Points
The tests integrate `tkv_fdb.go`, `tkv_test.go` shared raw KV tests, and broader metadata tests from the package.

## Risks and Test Signals
Risks are environmental: missing FDB build tag, missing cluster file, or unavailable local cluster. Passing tests signal that the FDB adapter can support both the generic KV contract and full metadata engine semantics.

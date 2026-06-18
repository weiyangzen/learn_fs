# sources/cloud-native/soci-snapshotter/metadata/reader_test.go

Purpose: test entry point and bbolt-backed test factory for metadata Reader behavior, plus direct tests for the generic `partition` helper.

Important APIs/types/functions: `TestMetadataReader` delegates to shared `testReader`. `newTestableReader` creates a temp bbolt DB, calls `NewReader`, and returns `testableReadCloser`. `TestPartition` checks chunking behavior for exact division, remainder, empty input, oversized chunks, zero chunk size, and negative chunk size.

Control flow: metadata tests are shared with other possible reader factories. The factory creates a temp file, opens bbolt, initializes the reader, and wraps cleanup. Partition tests call `partition` and compare nested slice shape and values manually.

State and persistence: creates temporary bbolt DB files and removes them on close. `testableReadCloser.Close` closes/removes the DB and then calls reader `Close`, which deletes the fsID bucket.

Dependencies/integration points: depends on bbolt and shared test utilities from `util_test.go`. It validates production `NewReader` through generated ztoc fixtures.

Risks: deferred `os.Remove(f.Name())` in `newTestableReader` runs before the returned close function; on Unix the open DB can continue using the unlinked file, but this is platform-sensitive. Close order calls DB close before reader Close, so bucket deletion may operate on a closed DB if reached; tests may tolerate this through ignored close errors.

Test signals: partition helper has focused coverage; full reader coverage is provided by `testReader` cases.

# sources/cloud-native/containerd/core/snapshots/storage/bolt_test.go

## Purpose
Connects the generic metastore test and benchmark suites to the BoltDB `MetaStore` implementation.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestMetastore` passes a temp `metadata.db` path to `NewMetaStore` and runs `MetaStoreSuite`. `BenchmarkSuite` does the same for `Benchmarks`. The blank `testutil` import ensures snapshot test flags are defined.

State is temporary Bolt database files created during tests/benchmarks. Dependencies include `filepath`, `testing`, and the local suite helpers.

The file verifies that the Bolt implementation satisfies the generic storage behavior. Risks are mostly in coverage: it delegates all assertions to the suite. Test signal is the full suite passing against real bbolt persistence.

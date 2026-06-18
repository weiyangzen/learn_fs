# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/reader_test.go

Purpose: Adapts broad metadata and filesystem conformance suites to the bbolt-backed metadata reader.

Important APIs tested: `NewReader`, `reader` as `testutil.TestableReader`, and the `metadata.Reader` interface through fs reader and layer suites.

Control flow: Each test constructs a runner that bridges custom testing interfaces to `*testing.T`. `newTestableReader` and `newStore` create a temp bbolt database, open it, instantiate `NewReader`, and wrap close behavior so the DB file is removed. `TestReader` invokes metadata testutil, `TestFSReader` invokes fs reader suite, and `TestFSLayer` invokes layer suite.

State and persistence: Temporary bbolt files hold metadata during each reader. Wrappers close the DB and remove the file.

Dependencies and integration: Integrates the DB metadata backend with shared packages `metadata/testutil`, `fs/reader`, and `fs/layer`.

Risks covered: Broad behavior such as lookup, attributes, file reads, chunk handling, and layer semantics are likely covered by the imported suites. The test file itself does not enumerate cases, so changes in upstream shared suites affect coverage. It does not test long-lived shared DB accumulation or concurrent readers beyond what the suites exercise.

Test signals: High-value integration coverage because the same suites can compare DB behavior against other metadata stores.

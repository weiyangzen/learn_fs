# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/packer_test.go

Purpose: exercises packer construction, local pack flow, push flow with mocked backend, chunk-dict parsing, compaction skips, binary lookup errors, blob hash parsing, logger creation, and backend config cleanup.

Important fixtures/APIs: `mockBuilder`, `setUpTmpDir`, `copyFile`, `New`, `Pack`, `getNewBlobsHash`, `getChunkDictBlobs`, `tryCompactParent`, `ensureNydusImagePath`, `getBlobsFromBootstrap`, and `dumpBlobBackendConfig`.

Control flow and state: tests create fake `nydus-image` files under `testdata`, copy canned `output.json`, replace the builder with a mock, inject mocked push backends, and assert returned local/remote paths. Cleanup tests verify temporary backend config files are zeroed/removed without panic.

Dependencies and integration points: testify mock/require, local filesystem, testdata JSON, OCI descriptors, packer pusher, logrus.

Risks and test signals: tests cover many error edges but use relative `testdata/TestName` directories. Successful compactor execution and real inspector output are not covered.

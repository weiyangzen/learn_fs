# sources/distributed-fs/beegfs-go/common/rst/store_test.go

Purpose: tests `ClientStore.UpdateConfig` initialization and immutability rules.

Important test is `TestUpdateConfig`. It creates a mock filesystem, a new client store, and an S3 RST config.

Control flow: first update initializes the store and should succeed. Subsequent calls attempt to modify the bucket, add an RST, and remove all RSTs; each must return `ErrConfigUpdateNotAllowed`.

State behavior under test is the transition from empty `clients` map to initialized map containing the S3 provider and implicit job builder, then rejecting later changes. Persistence is limited to in-memory provider state; no S3 calls are made during the tested config.

Dependencies include `testing`, `testify/assert`, mock filesystem, context, and Flex RST config messages.

Integration points are RST provider construction and protobuf config equality.

Risks: the test does not assert that the job builder was added or that `Get` returns expected providers. It does not cover attempts to use ID 0, same-config reload success after initialization, invalid RST type errors, or mock injection.

Test signals: clear coverage for the major policy that RST configuration cannot change after initial setup.

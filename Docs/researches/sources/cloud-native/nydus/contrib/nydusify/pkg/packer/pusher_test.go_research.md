# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/pusher_test.go

Purpose: validates backend config parsing and pusher upload sequencing with mocked backends.

Important fixtures/APIs: `mockBackend`, `ParseBackendConfig`, `ParseBackendConfigString`, `Pusher.Push`, and `NewPusher`.

Control flow and state: tests parse OSS/S3 configs from file and strings, reject unsupported backend types and invalid JSON, simulate pushing meta/blob files with URL descriptors, skip blob upload when blob ID is empty, upload parent blobs, and check constructor validation for output directories and backend initialization.

Dependencies and integration points: testify mock, local testdata output/backend config, OCI descriptors, backend interface types, and logrus.

Risks and test signals: tests do not simulate upload or finalize failures because mock `Finalize` always succeeds and `Upload` always returns nil error. They validate URL extraction and high-level ordering through mock expectations.

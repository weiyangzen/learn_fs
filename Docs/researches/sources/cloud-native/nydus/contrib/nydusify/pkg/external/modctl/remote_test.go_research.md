# sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/remote_test.go

Purpose: tests remote modctl handling using mocked registry remotes and in-memory tar data.

Important fixtures/APIs: `MockRemote`, local `readSeekCloser`, and tests for `RemoteHandler.Handle`, `GetModelConfig`, `setManifest`, `backend`, `NewRemoteHandler`, `initRemoteHandler`, `hackFileWrapper`, and `GetLayers`.

Control flow and state: the main handle test builds an in-memory tar with three files, attaches CRC annotations, and verifies emitted file attributes and backend metadata. It then supplies invalid CRC JSON and expects an error. Constructor tests monkey-patch default remote creation and initialization.

Dependencies and integration points: gomonkey, provider and remote packages, model spec JSON, snapshotter backend structs, OCI descriptors, tar archive readers, and environment variables for hack mode.

Risks and test signals: coverage confirms CRC propagation and invalid annotation rejection. It does not validate concurrent ordering determinism or plain HTTP fallback behavior. Some mocks omit methods not used by the tested path, so interface drift may only be caught at compile time.

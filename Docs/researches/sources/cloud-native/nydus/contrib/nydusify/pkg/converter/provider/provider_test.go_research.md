# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/provider_test.go

Purpose: broad regression coverage for the converter provider package, especially provider state helpers, local import/export paths, content store replacement, and the StreamContent adapter used by streaming copy flows.

Important APIs and behavior under test: `New`, `ContentStore`, `SetContentStore`, `UsePlainHTTP`, `SetPushRetryConfig`, `WithLocalSource`, `WithLocalTarget`, `Resolver`, `Image`, `NewRemoteCache`, `Import`, `Export`, `Pull`, `Push`, and most StreamContent methods. The test host function validates insecure routing for a sentinel reference.

Control flow and state: tests construct a provider with a temporary work directory, mutate provider fields through public helpers, and validate image descriptor lookup through the internal `images` map. Local source and target branches verify error behavior for missing tar files and successful creation of output tar files.

Dependencies and integration points: containerd content APIs, platform matchers, acceleration-service remote credentials, OCI descriptors, local filesystem tar import/export, and StreamContent in-memory storage.

Risks and test signals: coverage is strongest for state mutation and StreamContent edge cases. Several local push/export tests only assert file creation and tolerate provider export errors, so manifest correctness and real registry behavior remain integration risks.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/registry/ops.go -->
# sources/cloud-native/moby/internal/testutil/registry/ops.go

Purpose: option helpers for configuring the test registry fixture. Important APIs are `Htpasswd`, `Token`, `URL`, `WithStdout`, and `WithStderr`, each mutating `Config`. Control flow is simple option application: authentication, token endpoint, registry URL override, and process stream routing are configured before `NewV2` starts the registry. State lives in the pending registry config. Dependencies are the `Config` type and `io.Writer`. Risks are low, though option ordering can affect expected auth behavior. Test signal is through registry integration tests that need credentialed or token-backed registries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/registry/ops.go -->

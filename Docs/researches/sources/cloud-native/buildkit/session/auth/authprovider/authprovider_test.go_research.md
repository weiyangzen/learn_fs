<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authprovider_test.go -->
# sources/cloud-native/buildkit/session/auth/authprovider/authprovider_test.go

Purpose: verifies Docker auth provider cache behavior for registry tokens loaded from Docker config.

Important APIs, types, and functions: `TestFetchTokenCaching` creates a Docker config with Docker Hub registry token `hunter2`, fetches it, mutates config to `hunter3`, verifies default provider returns cached `hunter2`, then repeats with `ExpireCachedAuth` always true and verifies refreshed `hunter3`.

Control flow and state: test exercises `LoadAuthConfig` cache through `NewDockerAuthProvider` and `FetchToken`. It also validates Docker Hub host to config key mapping.

Dependencies and integration: uses Docker CLI config structs, generated auth request types, and testify assertions.

Risks and test signals: only static `RegistryToken` path is covered. OAuth network paths, TLS config, logger behavior, and token authority remain untested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authprovider_test.go -->

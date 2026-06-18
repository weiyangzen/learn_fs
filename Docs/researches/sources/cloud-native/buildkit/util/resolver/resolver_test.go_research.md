<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/resolver_test.go -->
# sources/cloud-native/buildkit/util/resolver/resolver_test.go

Purpose: validates construction of mirror registry host entries from daemon registry mirror config strings.

Important APIs and types: `TestNewMirrorRegistryHost` exercises `newMirrorRegistryHost` using config loaded by `cmd/buildkitd/config`.

Control flow: test parses a TOML registry config with mirrors with and without schemes and paths. For each mirror it asserts parsed host and resulting registry path, including joining mirror path under default `/v2`.

State and persistence: in-memory config parsing only.

Dependencies and integration: uses daemon config loader, `path.Join`, and `testify/require`.

Risks: coverage is narrow: no TLS config, insecure/plain HTTP, fallback, resolver pool, or auth host callback behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/resolver_test.go -->

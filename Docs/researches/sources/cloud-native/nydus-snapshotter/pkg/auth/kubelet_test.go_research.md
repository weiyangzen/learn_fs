# sources/cloud-native/nydus-snapshotter/pkg/auth/kubelet_test.go

Purpose: unit and integration-style tests for kubelet credential provider plugin loading, validation, matching, execution, and caching.

Important APIs and functions: helpers create temporary plugin binaries and kubelet credential provider config YAML: `setupKubeletProvider`, `buildAuthSection`, `createMockPlugin*`, `createMockCredentialProvider*`, `createMockProviderConfig`, and `setupMockProvider`. Tests cover `NewKubeletProvider`, `validateCredentialProvider`, `GetCredentials`, `InitKubeletProvider`, `urlsMatchStr`, cache eviction, `ValidUntil`, TTL behavior, `computeCacheKey`, and `parseRegistry`.

Control flow: mock plugins are shell scripts that consume stdin and emit a JSON `CredentialProviderResponse`. Tests create configs with match patterns, execute provider calls against image refs, then often remove plugin binaries to prove whether later calls hit cache or re-execute.

State and persistence: uses temp directories for plugin binaries/configs and mutates global `kubeletProvider`, restoring it in relevant tests. Cache behavior is observed through provider calls and direct `provider.cache` inspection in eviction tests.

Dependencies and integration points: exercises real process execution via `exec.CommandContext`, kubelet API structs, YAML marshal/unmarshal, and production URL matching/cache code.

Risks and gaps: shell-script mock plugins make tests Unix-like; there is no Windows equivalent in this file. Tests do not cover plugin timeout, stderr propagation in detail, malformed JSON responses, response kind validation, or concurrent cache access under plugin load.

Test signals: strong coverage for validation failures, first-plugin-wins overlap semantics, most-specific auth matching, no pointer-loop regression, idempotent global init, invalid URL/glob handling, zero/negative/positive TTL semantics, cache key type behavior, and `ValidUntil` bypass of too-short cached credentials.

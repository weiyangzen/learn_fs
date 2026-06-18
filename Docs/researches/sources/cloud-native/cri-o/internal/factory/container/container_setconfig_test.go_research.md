# sources/cloud-native/cri-o/internal/factory/container/container_setconfig_test.go

Purpose: validates container config initialization invariants.

Important APIs/types/functions: exercises `SetConfig`, `Config`, and `SandboxConfig`.

Control flow: tests assert success for a config with metadata/name and a sandbox config, failure for nil container config, empty config with nil metadata, empty metadata name, repeated config setting, and nil sandbox config.

State and persistence behavior: in-memory container object state only.

Dependencies/integration points: Ginkgo/Gomega and CRI API types.

Risks: does not cover already-set sandbox config independently of already-set container config, and does not assert specific error strings.

Test signals: strong coverage for constructor-style validation before later container setup steps rely on config presence.

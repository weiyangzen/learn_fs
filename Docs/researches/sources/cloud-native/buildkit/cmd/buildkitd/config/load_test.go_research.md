# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/load_test.go

Purpose: validates TOML decoding for a representative `buildkitd.toml` configuration covering root, logging compatibility fields, entitlements, gRPC/TLS, OTEL, OCI and containerd worker settings, GC policy variants, registry config, and DNS.

Important flow: `TestLoad` decodes an inline TOML string with nested tables and repeated `gcpolicy` entries, then asserts primitive values, pointer fields, labels with dotted keys, runtime options, bytes/percentage/duration parsing, registry mirror/TLS/keypair values, and DNS lists.

State and dependencies: no persisted files; it uses an in-memory buffer and the config loader. Dependencies are `time` and testify assertions.

Risks and test signals: the test is strong for schema/tag regression and text unmarshaling compatibility, especially percentage and unit values. It does not cover all newer config fields, invalid TOML, missing file handling, or default application performed in `cmd/buildkitd/main.go`.

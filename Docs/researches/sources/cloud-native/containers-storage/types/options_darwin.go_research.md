# sources/cloud-native/containers-storage/types/options_darwin.go

Purpose: Darwin storage path defaults and rootless overlay capability stub.

Important APIs and control flow: defines Linux-like default run and graph roots plus system and override config paths; `canUseRootlessOverlay` returns false.

State and persistence: no mutable state beyond `defaultOverrideConfigFile`.

Dependencies and integration: selected on Darwin builds and supplies symbols consumed by shared config-loading code.

Risks: paths may be less idiomatic for macOS than for Linux, but this package is generally used in container tooling where Linux compatibility paths are expected. Overlay is unavailable by default.

Test signals: compile coverage on Darwin validates symbol availability; behavior is mainly exercised through shared option tests where supported.

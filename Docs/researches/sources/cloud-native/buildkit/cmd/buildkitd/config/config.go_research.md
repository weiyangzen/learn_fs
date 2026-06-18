# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/config.go

Purpose: defines the TOML-backed BuildKit daemon configuration schema. It is the shared contract consumed by daemon startup, worker initializers, resolver setup, GC policy construction, CDI setup, frontend gating, provenance, and cache backends.

Important types: `Config` includes root path, deprecated debug/trace flags, insecure entitlements, proxy network, log, gRPC/TLS, OTEL, CDI, worker configs, registry resolver config, DNS, history, frontends, system tuning, provenance env dir, and cache config. Worker structs split OCI and containerd options, each embedding `GCConfig` and `NetworkConfig`. `GCPolicy`, `DiskSpace`, `Duration`, `DNSConfig`, `HistoryConfig`, frontend configs, and GHA cache config shape nested TOML sections.

State and dependencies: this file defines data only; persistence is in the TOML file and daemon root directories. It depends on GHA cache types and resolver registry config types.

Risks and test signals: schema tags are compatibility-sensitive because user config files depend on them. Deprecated fields remain for backward compatibility. `load_test.go` validates many nested TOML mappings, but not every field such as CDI, frontends, system tuning, provenance, or cache GHA.

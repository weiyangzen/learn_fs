# sources/cloud-native/soci-snapshotter/integration/config/etc/containerd/config.toml

Purpose: sample integration containerd configuration that disables unrelated plugins and registers SOCI as the snapshotter proxy plugin.

Important APIs and flow: declares containerd config `version = 2`, disables several snapshotter/storage/tracing/CRI plugins, and configures `[proxy_plugins.soci]` with type `snapshot` and the SOCI gRPC socket at `/run/soci-snapshotter-grpc/soci-snapshotter-grpc.sock`.

State and persistence: this TOML is static configuration consumed by containerd startup. It does not itself create runtime state.

Dependencies and integration: ties containerd's proxy snapshotter plugin system to the SOCI daemon socket. Disabling CRI in this config separates general integration tests from CRI-specific tests that generate their own containerd config.

Risks and test signals: socket path drift or proxy plugin type changes would prevent `ctr plugin ls` from reporting SOCI as healthy. Disabling plugins keeps the integration environment narrower but can hide interactions with CRI unless CRI-specific config is used.

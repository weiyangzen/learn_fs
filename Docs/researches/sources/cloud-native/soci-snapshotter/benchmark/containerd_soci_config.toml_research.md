# sources/cloud-native/soci-snapshotter/benchmark/containerd_soci_config.toml

Purpose: minimal containerd config for benchmarks using SOCI snapshotter as a proxy plugin.

Important APIs/types/functions: TOML `version = 2`, debug level `DEBUG`, `[proxy_plugins.soci]` with type `snapshot` and socket address `/tmp/soci-snapshotter-grpc/soci-snapshotter-grpc.sock`.

Control flow: containerd loads this config when benchmark code starts containerd for SOCI flows.

State and persistence: no persistent state; directs containerd to the SOCI snapshotter socket.

Dependencies/integration: used by `getContainerdProcess` in benchmark tests and Make benchmark targets.

Risks: hard-coded `/tmp` socket must match SOCI process startup. Debug logging can be verbose.

Test signals: SOCI benchmark startup and containerd proxy plugin registration.

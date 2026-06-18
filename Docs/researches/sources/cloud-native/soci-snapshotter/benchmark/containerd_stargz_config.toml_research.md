# sources/cloud-native/soci-snapshotter/benchmark/containerd_stargz_config.toml

Purpose: minimal containerd config for benchmarks using stargz snapshotter as a proxy plugin.

Important APIs/types/functions: TOML `version = 2`, debug level `DEBUG`, `[proxy_plugins.stargz]` with type `snapshot` and address `/tmp/containerd-stargz-grpc/containerd-stargz-grpc.sock`.

Control flow: containerd loads this file for Stargz benchmark flows and routes snapshot operations to the stargz socket.

State and persistence: no persistent state; configuration-only.

Dependencies/integration: used by `StargzFullRun` through `getContainerdProcess`.

Risks: hard-coded socket must match the stargz process. Debug logs may influence benchmark I/O.

Test signals: stargz benchmark run successfully creating containers with snapshotter `stargz`.

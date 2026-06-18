## sources/cloud-native/soci-snapshotter/benchmark/soci_config.toml

Purpose: minimal benchmark configuration enabling the CRI keychain for SOCI snapshotter benchmark runs.

Important settings: `[cri_keychain] enable_keychain = true` enables lookup through a CRI image service, and `image_service_path = "/tmp/containerd-grpc/containerd.sock"` points at the benchmark containerd socket.

Control flow: not executable itself; consumed by `soci-snapshotter-grpc` through the config loader when benchmark helpers launch the SOCI process.

State and persistence: no persistence; its values affect runtime credential resolution and socket dialing.

Dependencies and integration: matches `config.CRIKeychainConfig` TOML fields and integrates with the daemon's CRI keychain registration.

Risks and test signals: path is benchmark-environment-specific and will fail if the benchmark containerd socket is elsewhere. No standalone tests cover this file.

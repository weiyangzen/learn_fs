# sources/cloud-native/nydus-snapshotter/cmd/containerd-nydus-grpc/main.go

Purpose: main executable for the remote containerd Nydus snapshotter.

Flow: builds CLI flags, optionally prints version, fills default config, loads TOML if `--config` is set, applies CLI overrides, merges defaults, validates, prepares logging, processes global config, sets up root environment, logs startup metadata, and calls `Start`.

State/dependencies: reads config and filesystem paths, creates log directories/root, sets global logrus/containerd logging. Depends on urfave/cli, config, internal flags/logging, version, errdefs.

Integration points: systemd units, Makefile, CI, and deployment scripts invoke this binary.

Risks/tests: fatal logging exits on startup errors. CLI compatibility means command line overrides TOML, which can surprise config-only deployments.

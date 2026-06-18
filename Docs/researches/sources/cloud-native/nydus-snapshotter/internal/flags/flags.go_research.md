# sources/cloud-native/nydus-snapshotter/internal/flags/flags.go

Purpose: urfave/cli flag definitions for `containerd-nydus-grpc`.

APIs/flow: `Args` stores parsed values for root, address, snapshotter config, nydus binaries/config, overlayfs helper, daemon mode, fs driver, log level/stdout, and version printing. `buildFlags` wires CLI flags and alias `--config-path` for `--nydusd-config`; `NewFlags` returns flags plus backing args.

State/dependencies: parse state lives in `Args`; no filesystem access.

Integration points: main config parsing consumes these args with CLI-over-TOML precedence.

Risks/tests: default text is informational only, not a parsed value. Compatibility alias can be confused with snapshotter `--config`. Test verifies alias/root/log-level parsing.

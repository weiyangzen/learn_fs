# File Research: sources/cow-pools/bcachefs-tools/package-ci/bcachefs-package-ci.service

## Purpose
Systemd unit for running the bcachefs-tools package CI orchestrator.

## Behavior
- Runs as user `aptbcachefsorg`.
- Executes `/home/aptbcachefsorg/package-ci/bcachefs-package-ci`.
- Restarts on failure after 30 seconds.
- Sends logs to journald with identifier `bcachefs-package-ci`.
- Sets `RUST_LOG=info`, `XDG_RUNTIME_DIR`, and `HOME`.

## Notes
No additional systemd sandboxing is used because rootless podman handles namespaces and the service already runs unprivileged.

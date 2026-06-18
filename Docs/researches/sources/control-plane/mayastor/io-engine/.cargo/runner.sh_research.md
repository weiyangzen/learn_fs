<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/.cargo/runner.sh -->
# sources/control-plane/mayastor/io-engine/.cargo/runner.sh

Purpose: Privilege wrapper for running io-engine binaries/tests under Cargo with the Linux capabilities required by Mayastor/SPDK.

Important flow: captures command args, chooses `sudo -E --preserve-env=PATH` if not root, then invokes `capsh` with `cap_setpcap` plus ambient `cap_sys_admin`, `cap_ipc_lock`, `cap_sys_nice`, and `cap_sys_resource`, executing the original command via shell.

Dependencies: requires `sudo`, `capsh`, a working PATH under sudo, and the caller's environment variables to be preserved for SPDK/io-engine runtime configuration.

Integration points: referenced by `.cargo/config.toml` for Linux targets.

State and persistence: no persisted state; only affects process capabilities.

Risks and test signals: uses shell execution of captured args, so quoting matters. If sudo strips needed env vars despite `--preserve-env=PATH`, tests can fail in non-obvious ways. Healthy signal is binaries start without permission errors for hugepages, scheduling, resource limits, or IPC locking.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/.cargo/runner.sh -->

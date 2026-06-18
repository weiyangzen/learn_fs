# Research: sources/cloud-native/buildkit/examples/buildctl-daemonless/buildctl-daemonless.sh

Purpose: BusyBox-compatible wrapper that launches an ephemeral buildkitd, waits for it to become reachable, runs `buildctl`, then cleans up the daemon and temp directory.

Important flow: configurable environment variables choose `BUILDCTL`, retry count, `BUILDKITD`, `BUILDKITD_FLAGS`, and `ROOTLESSKIT`. The script creates a temp dir containing pid/addr/log, traps exit to kill/wait/remove, starts buildkitd on `/run/buildkit/buildkitd.sock` as root or `$XDG_RUNTIME_DIR/buildkit/buildkitd.sock` under rootlesskit as non-root, polls `buildctl --addr=$addr debug workers` with backoff, dumps daemon log on failure, and finally execs the requested buildctl command against the address.

State and dependencies: creates temporary files and a daemon process; buildkitd creates its own state according to flags/defaults. Depends on sh, mktemp, id, awk, expr, rootlesskit for non-root, buildkitd, and buildctl.

Risks and test signals: cleanup assumes pid file exists and kill is acceptable. Readiness probing depends on `debug workers`. No direct shell tests are listed.

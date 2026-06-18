# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/wsl2_linux.go

Purpose: Detects whether dockerd appears to run under WSL2 mirrored networking so bridge firewall code can apply WSL-specific loopback handling without executing external commands as root.

Important APIs and functions: `wslinfoPath` defaults to `/usr/bin/wslinfo` and is test-overridable. `isRunningUnderWSL2MirroredMode` returns true only when a `loopback0` link exists and `wslinfoPath` is a regular executable file.

Control flow: link lookup failures return false, except non-not-found errors are warned. File stat failures return false. The function uses mode bits instead of running `wslinfo --networking-mode`.

State and persistence: read-only; no persistent state.

Dependencies and integration points: depends on `nlwrap.LinkByName`, `netlink.LinkNotFoundError`, and containerd logging. Its result feeds bridge firewall workarounds for WSL2 mirrored mode.

Risks: heuristic can return false for unusual WSL installations without executable `wslinfo`, or true for environments that mimic `loopback0` plus executable `wslinfo`. The conservative design avoids privileged command execution.

Test signals: `wsl2_linux_test.go` covers loopback presence and executable/non-executable/no-file combinations.

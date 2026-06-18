<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/wsl2.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/wsl2.go

## Purpose
Adds/removes an iptables NAT exception for WSL2 mirrored networking loopback traffic.

## Important APIs, Types, And Functions
`mirroredWSL2Workaround` accepts an `iptables.IPVersion` and enable flag. It only acts for IPv4 and programs a `DOCKER` nat chain RETURN rule for `loopback0` traffic to `127.0.0.0/8`.

## Control Flow
Top-level chain setup calls this helper when hairpin mode is disabled and WSL2 mirrored networking is detected. The helper no-ops for IPv6 because WSL2 mirrored mode does not support Windows-to-Linux `::1` in this path.

## State And Persistence
State is a single IPv4 nat rule in the `DOCKER` chain. It is replayed during chain setup and removed during cleanup.

## Dependencies And Integration Points
Uses the iptables backend helpers and is paired with similar nftables logic. It integrates with docker-proxy behavior for loopback-bound published ports.

## Risks And Edge Cases
Without the rule, Windows-originated `127.0.0.1` traffic in WSL2 mirrored mode can be DNATed directly to a container with an unusable source address. The rule assumes the WSL2 interface name `loopback0`.

## Test Signals
Iptabler golden tests include WSL2-specific expected output only when IPv4, mirrored mode, and relevant loopback/proxy conditions apply.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/wsl2.go -->

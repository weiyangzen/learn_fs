<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/wsl2.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/wsl2.go

## Purpose
Adds nftables NAT exception logic for WSL2 mirrored networking loopback traffic.

## Important APIs, Types, And Functions
`mirroredWSL2Workaround` appends a rule to the shared `natChain` returning early for `iifname "loopback0"` and IPv4 destination `127.0.0.0/8`.

## Control Flow
`Nftabler.init` calls this helper only when hairpin is disabled, WSL2 mirrored mode is detected, and the table family is IPv4.

## State And Persistence
State is one nftables rule in the backend-owned table. It persists until the table is deleted or recreated.

## Dependencies And Integration Points
Uses internal `nftables.Modifier`. It mirrors the iptables WSL2 workaround and integrates with docker-proxy loopback behavior.

## Risks And Edge Cases
Assumes WSL2 uses `loopback0` and that IPv6 loopback from Windows is not supported in this path. Missing the rule can make Windows-originated localhost traffic reach containers with an unroutable source.

## Test Signals
Nftabler golden tests include WSL2-specific output only for combinations where IPv4 loopback/proxy behavior is affected.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/wsl2.go -->

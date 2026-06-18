<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/cleaner.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/cleaner.go

## Purpose
Detects and cleans iptables rules left by a previous daemon/backend, then exposes targeted cleanup hooks for restored networks, endpoints, and ports.

## Important APIs, Types, And Functions
`iptablesCleaner` stores top-level `firewaller.Config`. `NewCleaner` checks built-in FORWARD jumps for Docker chains, removes top-level jumps and user-defined chains, warns about `FORWARD` policy DROP, and returns a cleaner when work was done. `DelNetwork`, `DelEndpoint`, and `DelPorts` reconstruct lightweight `network` objects and call backend removal methods.

## Control Flow
On startup, if switching away from iptables, the new backend can obtain a cleaner. Immediate cleanup removes chains and jumps that can be identified globally. Later, when persisted networks/endpoints/ports are replayed, the cleaner removes rules that require bridge interface names or endpoint addresses.

## State And Persistence
No repo state is persisted. Host iptables state is mutated. The returned cleaner carries only enough config to delete per-family rules matching restored bridge configuration.

## Dependencies And Integration Points
Uses `iptables`, `firewaller`, containerd logging, and iptabler network/port/endpoint helpers. Paired with `nftabler.SetFirewallCleaner` and bridge store live-restore.

## Risks And Edge Cases
Built-in chain rules cannot be flushed indiscriminately because that would affect non-Docker firewall policy. Cleanup is best-effort and ignores many deletion errors. A remaining DROP policy on `FORWARD` may still break traffic accepted by nftables.

## Test Signals
`TestCleanupIptableRules` verifies Docker chains are flushed/removed as expected across IPv4 and IPv6 in an isolated namespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/cleaner.go -->

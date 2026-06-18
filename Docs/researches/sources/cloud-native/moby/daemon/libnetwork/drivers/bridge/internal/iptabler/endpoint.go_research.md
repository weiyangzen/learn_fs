<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/endpoint.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/endpoint.go

## Purpose
Programs per-endpoint direct-access filtering for the iptables backend.

## Important APIs, Types, And Functions
`AddEndpoint` and `DelEndpoint` call `modEndpoint`. `filterDirectAccess` adds or deletes raw table `PREROUTING` rules that allow trusted interfaces and drop packets addressed directly to container IPs from untrusted interfaces.

## Control Flow
For each valid IPv4/IPv6 endpoint address and enabled family, `modEndpoint` delegates to `filterDirectAccess`. The filter is skipped for internal, unprotected, routed, daemon-wide direct-routing, or raw-disabled configurations. Otherwise it creates ACCEPT rules for trusted interfaces and a DROP rule for traffic not arriving from the bridge.

## State And Persistence
State is host iptables raw table state keyed by endpoint IP and bridge/trusted interface names. It is intentionally endpoint-scoped so direct-routed traffic is blocked even before an endpoint becomes a gateway for published ports.

## Dependencies And Integration Points
Uses `iptables`, `firewaller.NetworkConfigFam`, `rawRulesDisabled`, and `appendOrDelChainRule`. Called during endpoint create/delete and live-restore endpoint replay.

## Risks And Edge Cases
`DOCKER_INSECURE_NO_IPTABLES_RAW=1` disables these rules and weakens direct-access protection. Trusted interface names become part of security policy. Config changes across live-restore deliberately force deletion when direct routing becomes allowed or raw rules are disabled.

## Test Signals
Iptabler golden tests include endpoint add/delete and raw rule output across routed, unprotected, internal, and WSL2-related combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/endpoint.go -->

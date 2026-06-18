<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler.go

## Purpose
Initializes and manages top-level iptables chains used by Docker bridge networking.

## Important APIs, Types, And Functions
Constants define Docker chains: `DOCKER`, `DOCKER-FORWARD`, `DOCKER-BRIDGE`, `DOCKER-CT`, `DOCKER-INTERNAL`, and legacy isolation chains. `Iptabler` holds `firewaller.Config`. `NewIptabler` initializes IPv4/IPv6 chains and reload hooks. `FilterForwardDrop` sets the built-in `FORWARD` policy to DROP. `setupIPChains`, `deleteLegacyTopLevelRules`, `programChainRule`, and `appendOrDelChainRule` perform core rule management.

## Control Flow
Initialization removes old chains, creates NAT/filter chains, adds NAT PREROUTING/OUTPUT jumps to `DOCKER`, installs filter FORWARD jumps into Docker chains, adds WSL2 loopback handling when needed, and deletes legacy top-level rules. IPv6 setup logs and continues on kernel/module failure so IPv4 daemon startup can proceed.

## State And Persistence
State is global host iptables chain/rule state. Reload callbacks replay chain creation and default DROP policy after firewall reloads. Failure cleanup removes newly created chains and jump rules where possible.

## Dependencies And Integration Points
Uses `iptables`, `modprobe`, `firewaller`, and containerd logging. It is selected by bridge driver configuration and provides network objects implemented in `network.go`.

## Risks And Edge Cases
Global chain mutation is security-sensitive and can interact with firewalld and user policies. IPv6 setup may silently degrade to logged warnings. Legacy rule deletion is necessary for upgrades but must avoid deleting unrelated user rules.

## Test Signals
`iptabler_test.go` checks cleanup and broad golden snapshots; `network_test.go` checks rule programming, setup, and outgoing NAT variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler.go -->

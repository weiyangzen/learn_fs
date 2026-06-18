<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler_test.go

## Purpose
Golden-tests the nftables backend across the same major policy dimensions as the iptables backend.

## Important APIs, Types, And Functions
`TestNftabler` enables the internal nftables mode and iterates boolean flags for IPv4, IPv6, hairpin, internal, ICC, masquerade, SNAT, localhost binding, and WSL2 mirrored mode across gateway modes. `testNftabler` initializes the backend, adds a network, endpoint, and port bindings, checks `nft list table` output, then deletes all objects and checks cleaned state.

## Control Flow
Each subtest creates an isolated namespace, chooses a shared golden result name for irrelevant combinations, creates `NewNftabler`, adds/removes network objects, and compares `ip`/`ip6` family table output.

## State And Persistence
Only test namespace nftables state is mutated. Expected outputs are persisted as golden files under backend testdata.

## Dependencies And Integration Points
Uses internal `nftables.Enable/Disable`, `netnsutils`, `icmd`, `golden`, `firewaller`, and `types.PortBinding`. Exercises all nftabler implementation files together.

## Risks And Edge Cases
The test currently avoids parallelism because cgo/libnftables behavior and shared golden files can be problematic. Output normalization handles nft priority wording differences.

## Test Signals
Passing golden checks signal stable nft table construction, network chain setup, endpoint filtering, port DNAT/forwarding, hairpin masquerade, WSL2 loopback exceptions, and cleanup back to the expected baseline.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler_test.go -->

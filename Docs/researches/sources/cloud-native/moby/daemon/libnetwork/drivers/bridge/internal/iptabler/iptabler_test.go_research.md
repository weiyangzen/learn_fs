<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler_test.go

## Purpose
Validates iptables backend cleanup and rule output over a large policy matrix.

## Important APIs, Types, And Functions
`TestCleanupIptableRules` verifies `removeIPChains`. `TestIptabler` enumerates booleans for IPv4, IPv6, hairpin, internal, ICC, masquerade, SNAT, localhost binding, and WSL2 mirrored mode across gateway modes. `testIptabler` initializes the backend, adds a network, endpoint, and port bindings, compares `iptables-save`/`ip6tables-save` output to golden files, then deletes everything and checks cleaned state.

## Control Flow
Tests run in isolated namespaces, skip when host firewalld interferes, generate expected-result names that collapse irrelevant dimensions, and dump raw/filter/nat tables explicitly to reduce backend ordering differences.

## State And Persistence
Temporary iptables state is created and destroyed in the test namespace. Golden files under backend testdata persist expected rule output for many combinations.

## Dependencies And Integration Points
Uses `iptables`, `netnsutils`, `gotest.tools/golden`, `icmd`, and `types.PortBinding`. It covers `Iptabler`, network, endpoint, port, and WSL2 helpers together.

## Risks And Edge Cases
Rule dump order can differ between iptables backends, so comments are stripped and tables are dumped separately. The matrix is broad but expensive; firewalld on the host can invalidate namespace assumptions.

## Test Signals
Passing golden checks signal stable cleanup, NAT/filter/raw rule generation, WSL2 exception behavior, localhost binding filtering, and equivalence of add/delete lifecycle to a known cleaned baseline.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/iptabler_test.go -->

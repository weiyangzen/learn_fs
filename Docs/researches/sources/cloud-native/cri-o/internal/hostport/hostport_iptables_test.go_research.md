# sources/cloud-native/cri-o/internal/hostport/hostport_iptables_test.go

## Purpose
Tests iptables hostport rule construction and cleanup using the in-memory fake iptables backend.

## Important APIs, Types, And Functions
- Defines expected IPv4 and IPv6 hostport rule sets.
- `checkIPTablesRules` compares hostport-related `iptables-save` output against expected sets.
- Exercises `ensureKubeHostportChains`, `getHostportChain`, `hostportManagerIPTables.Add`, and `hostportManagerIPTables.Remove`.

## Control Flow
Tests first verify base chains and jump rules, then validate hash-derived chain names are distinct for different ports/prefixes. IPv4 and IPv6 tests instantiate fake managers, add all shared test cases, compare generated `KUBE-HOSTPORTS`, `CRIO-HOSTPORTS-MASQ`, `KUBE-HP-*`, and `CRIO-MASQ-*` rules, remove all mappings, and assert no hostport rules remain.

## State And Persistence
Mutates fake in-memory NAT tables. Expected rule arrays document the persistent kernel state that real iptables would receive.

## Dependencies And Integration Points
Depends on shared `testCasesV4`/`testCasesV6`, fake iptables normalization, Kubernetes sets for comparison, and CRI-O iptables constants/types.

## Risks And Edge Cases
Expected rules are intentionally exact and may fail on harmless ordering/formatting changes unless the comparison remains set-based. Hash outputs are pinned, which protects cleanup compatibility but makes intended hash changes disruptive.

## Test Signals
Strong regression signal for iptables rule generation, IPv6 bracket formatting, HostIP filtering, SCTP support, duplicate host ports across IPs/protocols, and removal.

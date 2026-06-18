# sources/cloud-native/cri-o/internal/hostport/hostport_iptables.go

## Purpose
Implements the iptables backend for CRI-O hostport mappings. It creates per-pod/per-port NAT chains for DNAT and hairpin masquerade, preserves unrelated hostport state, and removes matching chains atomically through iptables-restore.

## Important APIs, Types, And Functions
- Constants define `KUBE-HOSTPORTS`, `KUBE-HP-*`, `CRIO-HOSTPORTS-MASQ`, and `CRIO-MASQ-*` chain names.
- `hostportManagerIPTables` wraps `utiliptables.Interface` plus a mutex.
- `newHostportManagerIPTables`, `Add`, `Remove`, `syncIPTables`, `ensureKubeHostportChains`, `getHostportChain`, `getExistingHostportIPTablesRules`, `getChainLines`, `readLine`, `filterRules`, `filterChains`, and `writeLine` implement backend behavior.

## Control Flow
`Add` ensures base hostport and masquerade chains, locks, reads current NAT hostport chains/rules, builds new chain declarations and insertion rules for every mapping, adds DNAT rules optionally constrained by `HostIP`, adds hairpin MASQUERADE rules, filters out old copies of the same chains, appends remaining existing hostport state, and restores the composed NAT table. `Remove` locks, computes target chain names from mappings, filters out rules mentioning those chains, emits existing chain declarations, emits `-X` deletes for existing target chains, and restores. Chain names are stable SHA-256/base32 hashes of sandbox ID, host port, protocol, and host IP.

## State And Persistence
Persists hostport behavior in kernel iptables NAT tables. It reads current state through `iptables-save` and writes through `iptables-restore --noflush --counters`. The manager mutex serializes operations within the process; iptables package handles command-level locking.

## Dependencies And Integration Points
Uses CRI-O internal iptables abstraction, Kubernetes-derived rule formatting, `net.JoinHostPort` for IPv6-safe destinations, and CRI hostport `PortMapping`. It is selected by `meta_hostport_manager.go` when nftables is unavailable or for legacy cleanup.

## Risks And Edge Cases
Changing `getHostportChain` breaks cleanup of existing rules. Rule filtering uses substring matching on chain names, so chain-name uniqueness matters. `getChainLines` can panic on malformed chain lines without spaces. Broad hostport jump rules must remain ordered behind kube-services assumptions. HostIP wildcard handling only recognizes empty, `0.0.0.0`, and `::`. Atomicity is limited to composed restore plus process mutex.

## Test Signals
`hostport_iptables_test.go` validates base chain setup, hash uniqueness, IPv4/IPv6 DNAT/SNAT rule generation, hostIP-specific rules, same host port on different IPs/protocols, and removal back to an empty hostport rule set.

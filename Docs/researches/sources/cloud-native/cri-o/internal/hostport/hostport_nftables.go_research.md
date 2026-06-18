# sources/cloud-native/cri-o/internal/hostport/hostport_nftables.go

## Purpose
Implements the nftables backend for CRI-O hostport mappings using nft maps and sets rather than per-port chains.

## Important APIs, Types, And Functions
- Constants define the `crio-hostports` table, `hostports` map, `hostipports` map, and `hairpins` set.
- `hostportManagerNFTables` wraps a `knftables.Interface`, family, and mutex.
- `newHostportManagerNFTables`, `Add`, `Remove`, `hashSandboxID`, and `ensureHostPortsTable` implement backend behavior.

## Control Flow
`Add` locks, creates a transaction, ensures the table/chains/maps/set and static rules exist, hashes the sandbox ID into a comment, then adds map elements for wildcard hostports or HostIP-specific hostports and a hairpin set element. `Remove` lists existing elements from both maps and the hairpin set, deletes elements whose comment matches the sandbox hash, and runs the transaction only if there is work. `ensureHostPortsTable` creates IPv4 or IPv6-specific nftables objects and flushes/repopulates static chains while preserving dynamic map/set elements.

## State And Persistence
Persists hostport mappings in kernel nftables table elements. The sandbox hash comment is the persistent key for IP-independent removal. Static chains are idempotently recreated on Add.

## Dependencies And Integration Points
Uses `sigs.k8s.io/knftables` for typed nftables transactions. Selected preferentially by `meta_hostport_manager.go` when available. Supports IPv4 and IPv6 families with family-specific address types and rule syntax.

## Risks And Edge Cases
Comment hash collisions are possible but unlikely; a collision would over-delete mappings. `Remove` ignores the supplied mapping details and deletes all elements for the sandbox comment. Ensuring static chains flushes chains but not dynamic elements. Errors listing maps/sets other than not-found abort removal.

## Test Signals
`hostport_nftables_test.go` verifies table/rule layout, IPv4/IPv6 element generation, HostIP-specific map use, hairpin entries, and cleanup to no elements.

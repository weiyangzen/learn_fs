# sources/cloud-native/cri-o/internal/hostport/hostport_nftables_test.go

## Purpose
Tests nftables hostport table creation, element generation, and removal for IPv4 and IPv6.

## Important APIs, Types, And Functions
- Expected element arrays pin map/set entries for IPv4 and IPv6.
- `checkNFTablesElements` compares fake nftables dump elements against expectations.
- Exercises `ensureHostPortsTable`, `hostportManagerNFTables.Add`, and `hostportManagerNFTables.Remove`.

## Control Flow
The table test creates a fake nftables transaction, runs `ensureHostPortsTable`, and compares the static table/chains/maps/set/rules dump. IPv4 and IPv6 tests add all shared fixture mappings to a fake manager, compare only dynamic `add element` lines, remove all mappings, and assert no elements remain.

## State And Persistence
Mutates `knftables.Fake` in-memory state. Expected dump strings document intended persistent nftables kernel objects.

## Dependencies And Integration Points
Uses `knftables.Fake`, Kubernetes set comparison, and shared hostport test fixtures. Confirms backend behavior used by the meta manager.

## Risks And Edge Cases
Exact static dump expectations are sensitive to knftables formatting. The tests validate normal add/remove paths but do not inject list/run failures or comment hash collision cases.

## Test Signals
Strong signal for nftables syntax, table idempotence assumptions, IPv6 family handling, HostIP map ordering, and sandbox-comment cleanup.

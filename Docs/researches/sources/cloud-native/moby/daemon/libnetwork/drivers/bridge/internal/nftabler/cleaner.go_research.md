<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/cleaner.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/cleaner.go

## Purpose
Deletes nftables rules created by a previous nftables bridge firewaller and stores a cross-backend cleaner on the current `Nftabler`.

## Important APIs, Types, And Functions
`Cleanup` calls `tryCleanup` for enabled IPv4/IPv6 families. `tryCleanup` runs `nft delete table <family> docker-bridges`. `SetFirewallCleaner` stores a `firewaller.FirewallCleaner` for targeted cleanup of old backend rules as networks/endpoints/ports are restored.

## Control Flow
Startup cleanup is table-level: delete the whole Docker bridge table for each enabled family and log success or the expected absence. During normal setup, `Nftabler` uses its `cleaner` field in network/endpoint/port methods before adding new nftables rules.

## State And Persistence
Host nftables table state is mutated. No repository state is stored. Cleaner state is an in-memory bridge between old and new firewall implementations.

## Dependencies And Integration Points
Uses internal `nftables.RunCmd`, `firewaller.Config`, and containerd logging. Integrated with bridge driver backend switching and store live-restore.

## Risks And Edge Cases
Table deletion is coarse but safe because the table is backend-owned. Errors for missing tables are logged at info level, so unexpected nft command failures need log inspection.

## Test Signals
Covered indirectly by nftabler golden tests and backend-switch cleanup flows; direct tests would assert table absence after `Cleanup`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/cleaner.go -->

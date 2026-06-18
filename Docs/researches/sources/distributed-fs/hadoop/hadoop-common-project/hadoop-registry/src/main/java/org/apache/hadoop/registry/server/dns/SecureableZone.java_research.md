# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/SecureableZone.java

## Purpose
`SecureableZone` extends xbill `Zone` with record tracking needed for limited DNSSEC negative-response support through NXT records.

## Important APIs and types
Constructors mirror `Zone` constructors for zone transfers, remote transfers, master files, and record arrays. It overrides `addRecord` and `removeRecord` to maintain a local `List<Record> records`. `getNXTRecord(Record queryRecord, Zone zone)` computes an NXT record for a query insertion point.

## Control flow
On add/remove, the superclass zone is updated and the local records list is updated. `getNXTRecord` sorts the tracked records, binary-searches the query, chooses the insertion/base record, gathers existing RRset types at that base name, and returns an `NXTRecord` with the zone SOA minimum TTL.

## State and persistence behavior
State is in-memory only. The `records` list mirrors dynamic zone changes after construction, but constructor-loaded records may not be copied into the list until added through overridden methods.

## Dependencies and integration points
It depends on xbill DNS `Zone`, `Record`, `RRset`, `SetResponse`, `NXTRecord`, and transfer classes. `RegistryDNS.configureZone()` creates `SecureableZone` instances, and DNSSEC NXDOMAIN handling calls `getNXTRecord`.

## Risks and test signals
If `records` is null or incomplete for zones loaded from files/arrays, `getNXTRecord` may fail or produce incomplete NXT data. The list is not synchronized itself; callers rely on `RegistryDNS` locks. Tests should cover constructor-seeded zones, dynamic add/remove, NXT generation before/after first mutation, sorted insertion points, and concurrent access through `RegistryDNS`.

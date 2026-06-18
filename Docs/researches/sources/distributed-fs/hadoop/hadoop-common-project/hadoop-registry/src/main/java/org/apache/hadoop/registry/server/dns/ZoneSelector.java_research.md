# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ZoneSelector.java

## Purpose
`ZoneSelector` abstracts how DNS processors find the best matching DNS zone for a generated record name.

## Important APIs and types
The single method `findBestZone(Name name)` returns an xbill `Zone`.

## Control flow
`BaseServiceRecordProcessor.manageDNSRecords()` calls this method for every generated `Name` before executing a record add/remove command. `RegistryDNS` implements it by exact zone lookup followed by suffix lookup across labels.

## State and persistence behavior
The interface has no state. Implementations usually read in-memory zone maps.

## Dependencies and integration points
It depends on xbill `Name` and `Zone` and decouples processors from the concrete `RegistryDNS` zone map.

## Risks and test signals
A null result means record commands must handle no matching zone. Tests should verify exact, suffix, reverse-zone, and no-match behavior through the `RegistryDNS` implementation.

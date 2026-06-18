# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RegistryDNSServer.java

## Purpose
`RegistryDNSServer` composes registry ZooKeeper operations and `RegistryDNS` into a lifecycle-managed DNS server that reacts to registry path changes.

## Important APIs and types
It extends `CompositeService`. State includes `RegistryDNS registryDNS`, `RegistryOperationsService registryOperations`, and `ConcurrentMap<String, ServiceRecord> pathToRecordMap`. Key methods are `serviceInit`, `serviceStart`, `manageRegistryDNS`, `processServiceRecords`, `processServiceRecord`, `launchDNSServer`, and `main`.

## Control flow
Initialization creates a registry operations child and a DNS child, using `DNSOperationsFactory` if a DNS instance was not injected. Start calls `manageRegistryDNS()`, which instantiates a Curator cache, registers a `PathListener`, starts the cache, and maps node additions to record extraction and DNS registration. Node removals look up the prior record in `pathToRecordMap` and delete generated DNS records.

## State and persistence behavior
The server reads persistent ZooKeeper service records via `RegistryOperationsService`. It maintains a transient map from relative registry path to the last seen `ServiceRecord` so delete events have enough data to remove DNS records. DNS state remains in the `RegistryDNS` in-memory zones.

## Dependencies and integration points
It integrates Curator path listening, registry path utilities, `RegistryUtils.extractServiceRecords`, `RegistryDNS`, Hadoop service launch/shutdown utilities, `RegistryConfiguration`, and generic options parsing.

## Risks and test signals
Path normalization is central: add events process relative paths but delete events use `path.substring(registryRoot.length())` to look up cached records. Tests should verify add/delete path keys match. If listener setup fails, DNS support is disabled with a warning but the service remains started. Tests should cover initial cache events, updates, deletes, malformed service records, injected DNS instances, shutdown hooks, and command-line launch failure paths.

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RecordCreatorFactory.java

## Purpose
`RecordCreatorFactory` maps DNS record type codes to small creator objects that build xbill DNS `Record` instances with the configured TTL.

## Important APIs and types
Static state is `ttl`, set by `setTtl(long)`. `getRecordCreator(int)` supports A, AAAA, CNAME, TXT, PTR, and SRV. Nested `RecordCreator<R,T>` defines `create(Name,T)`. Concrete creators build `ARecord`, `AAAARecord`, `CNAMERecord`, `TXTRecord`, `PTRRecord`, and `SRVRecord`. `HostPortInfo` carries SRV target host and port.

## Control flow
`BaseServiceRecordProcessor.manageDNSRecords()` selects a creator per record type, passes descriptor names and targets, and sends the created record to a registry command.

## State and persistence behavior
TTL is process-global static state for all records produced by this factory. Created records are in-memory objects until added to DNS zones by `RegistryDNS`.

## Dependencies and integration points
It depends on xbill DNS record classes and Java `InetAddress`. `RegistryDNS.initializeZones()` sets TTL from configuration before service records are processed.

## Risks and test signals
The static TTL can leak between tests or multiple service instances in one JVM. SRV priority and weight are hard-coded to 1. Tests should verify each supported type creation, unknown type rejection, TTL propagation, and SRV target/port behavior.

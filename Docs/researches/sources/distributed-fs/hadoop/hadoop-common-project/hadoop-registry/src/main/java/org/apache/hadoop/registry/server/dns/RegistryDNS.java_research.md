# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RegistryDNS.java

## Purpose
`RegistryDNS` is the DNS service that reflects YARN registry service records into xbill DNS zones and answers UDP/TCP DNS queries. It implements `DNSOperations` for register/delete and `ZoneSelector` for processor zone lookup.

## Important APIs and types
The class extends `AbstractService`. Major state includes an executor, read/write zone lock, `domainName`, `ttl`, DNSSEC flag and key data, `dnsKeyRecs`, `zones`, `bindHost`, channel initialization flag, and resolver update state. Important methods include `initializeChannels`, `serviceInit`, `initializeZones`, reverse-zone helpers, `configureZone`, DNSSEC setup/signing, NIO TCP/UDP serving, `generateReply`, `addAnswer`, `remoteLookup`, `findExactMatch`, `findBestZone`, `register`, `delete`, and nested `RegistryCommand` implementations.

## Control flow
Service initialization updates default resolvers, reads the DNS domain, builds zones from files/configuration, creates primary and reverse zones, and opens UDP/TCP listeners. Query serving parses DNS messages, rejects unsupported opcodes/types, answers from local zones with authoritative data when possible, falls back to upstream lookup when local lookup fails, adds glue/additional records, and handles AXFR over TCP. Registry mutations route through `op()`, which selects a container or application service-record processor based on `yarn:persistence`, then executes add/remove commands for generated records.

## State and persistence behavior
The DNS zone map is in-memory service state. Records are added and removed dynamically as registry events arrive. DNSSEC keys are loaded from configuration/files and signatures are added to RRsets when enabled. Zone files can seed initial zones. No DNS state is written back to ZooKeeper by this class.

## Dependencies and integration points
It uses many xbill DNS classes, Hadoop `DNSOperations`, `ServiceRecord`, YARN attributes, Hadoop executor/thread helpers, `ReverseZoneUtils`, `SecureableZone`, `RecordCreatorFactory`, and service-record processors. It is launched by `RegistryDNSServer` or pre-initialized by `PrivilegedRegistryDNSStarter`.

## Risks and test signals
Concurrency centers on `ReentrantReadWriteLock`; add/remove paths should consistently hold write locks, but `removeRecordCommand` removes without the wrapper lock in the read source, so concurrent query/mutation tests are important. Remote lookup creates a new single-thread executor per lookup. DNSSEC code depends on key config and file format and the file as read contains suspicious duplicated method signature text in `enableDNSSECIfNecessary`; compilation is a critical signal. Query tests should cover UDP/TCP, EDNS DO flag, CNAME recursion, NXDOMAIN/NXRRSET, SOA/NS authority, reverse zones, split reverse zones, DNSSEC signing/NXT, AXFR, and service-record registration/delete symmetry.

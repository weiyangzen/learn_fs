<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolver.java

## Purpose
`DomainNameResolver` abstracts service discovery for Hadoop components that need to resolve domain names to addresses or hostnames, including NameNodes, routers, and resource managers.

## Important APIs and Types
It declares `getAllByDomainName`, `getHostnameByIP`, and `getAllResolvedHostnameByDomainName`.

## Control Flow
The interface describes a two-step secure mode flow: forward-resolve a domain to all IP addresses, then optionally reverse-resolve each IP to an FQDN for service principals.

## State and Persistence
State is implementation-defined. Implementations may use DNS, ZooKeeper, static maps, or other discovery mechanisms.

## Dependencies and Integration Points
`DomainNameResolverFactory` instantiates configured implementations. Hadoop failover proxy and HA client code can use the abstraction to discover all endpoints behind a logical domain.

## Risks and Test Signals
The contract does not define ordering, duplicate handling, caching, or null semantics. Implementation tests should cover multi-address domains, reverse lookup behavior, `useFQDN` choices, `UnknownHostException`, and service-specific configuration integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolver.java -->

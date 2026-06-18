<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSDomainNameResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSDomainNameResolver.java

## Purpose
`DNSDomainNameResolver` is the default `DomainNameResolver` implementation. It uses Java DNS for forward lookup and reverse lookup to produce IP addresses or fully qualified host names.

## Important APIs and Types
It implements `getAllByDomainName`, `getHostnameByIP`, and `getAllResolvedHostnameByDomainName`.

## Control Flow
Forward lookup delegates to `InetAddress.getAllByName`. Reverse lookup starts with `InetAddress.getCanonicalHostName`, strips a trailing dot, and if Java returns the raw IP address from cache, attempts `DNS.reverseDns`. Bulk resolution first resolves all addresses, then either reverse-resolves each to FQDNs or returns host address strings depending on `useFQDN`.

## State and Persistence
The class has no mutable state. It uses JVM and OS DNS caches indirectly.

## Dependencies and Integration Points
`DomainNameResolverFactory` creates this as the default resolver. HA clients, routers, and secure environments use it to convert service hostnames into IPs or FQDNs for Kerberos-aware connection logic.

## Risks and Test Signals
Reverse DNS failures after Java returns an IP are logged and the IP-like host may be returned. IPv6 reverse fallback inherits `DNS.reverseDns` limitations. Tests should cover multi-address forward lookup, FQDN mode, non-FQDN mode, trailing dot stripping, IP-cache fallback, and reverse lookup failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSDomainNameResolver.java -->

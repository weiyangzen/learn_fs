# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/MockDomainNameResolver.java

## Purpose
Test `DomainNameResolver` implementation with deterministic forward and reverse DNS behavior for Hadoop network tests.

## Important APIs, Types, And Functions
Implements `getAllByDomainName()`, `getHostnameByIP()`, `getAllResolvedHostnameByDomainName()`, and testing setter `setAddressMap()`. Constants define the default domain, two IP byte arrays/strings, and two FQDNs.

## Control Flow
Constructor builds `InetAddress` objects for `10.1.1.1` and `10.1.1.2`, maps `test.foo.bar` to both, and maps each address to a hostname. Forward lookup throws `UnknownHostException` for unknown domains. Resolved-hostname lookup returns either FQDNs from `ptrMap` or raw IP strings depending on `useFQDN`.

## State And Persistence Behavior
State is per-instance maps: a `TreeMap` for domain to addresses and a `HashMap` for address to PTR name. `setAddressMap()` can replace forward mappings for tests.

## Dependencies And Integration Points
Used through `DomainNameResolverFactory` when `HADOOP_DOMAINNAME_RESOLVER_IMPL` points at this class.

## Risks
`UNKNOW_DOMAIN` is misspelled but public and used by tests. Replacing only `addrs` with `setAddressMap()` can make forward and reverse maps inconsistent. `getHostnameByIP()` returns null for missing PTRs rather than throwing.

## Test Signals
Default resolver should return exactly two addresses for `DOMAIN`, FQDNs when requested, IP strings otherwise, and throw for `UNKNOW_DOMAIN`.

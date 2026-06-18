# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestDNSDomainNameResolver.java

## Purpose
Tests that `DNSDomainNameResolver.getHostnameByIP()` returns the canonical hostname even when an `InetAddress` instance was constructed with an unresolved host string equal to its IP address.

## Important APIs, Types, And Functions
Uses static `DNSDomainNameResolver DNR`, `InetAddress.getLocalHost()`, `InetAddress.getByAddress(String, byte[])`, and `getHostnameByIP()`.

## Control Flow
The test obtains localhost, assumes canonical name lookup is supported, builds an unresolved-style address whose host name is the IP string, calls the resolver, and asserts the result differs from the IP but equals localhost's canonical host name.

## State And Persistence Behavior
No persistent state beyond JVM/OS DNS caches.

## Dependencies And Integration Points
Exercises resolver behavior around Java `InetAddress` caching and canonical reverse lookup.

## Risks
Skipped when local canonical hostname equals host address. Results depend on OS DNS/PTR configuration.

## Test Signals
Expected signal is canonical name recovery despite the input address initially reporting its host name as the numeric IP.

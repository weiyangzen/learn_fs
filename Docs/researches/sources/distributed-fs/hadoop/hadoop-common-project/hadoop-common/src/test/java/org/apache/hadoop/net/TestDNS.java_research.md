# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestDNS.java

## Purpose
Tests Hadoop `DNS` utility behavior for local host/IP lookup, caching, null/default parameters, reverse DNS, hosts-file fallback, invalid interfaces, and localhost resolution.

## Important APIs, Types, And Functions
Uses `DNS.getDefaultHost()`, `getDefaultIP()`, `getIPs()`, `reverseDns()`, `getCachedHostname()`, `setCachedHostname()`, and helper `getLoopbackInterface()`.

## Control Flow
Tests call default host/IP lookups, compare repeated calls for speed and equality, validate null/default DNS server equivalence, verify unknown interface exceptions, perform reverse DNS with assumptions on unsupported environments, and test fallback behavior by forcing cached hostname to a dummy value and using invalid DNS server `0.0.0.0`.

## State And Persistence Behavior
`DNS.cachedHostname` is static process state. Fallback tests save and restore it in `finally`. Network interface and resolver state come from the host OS.

## Dependencies And Integration Points
Depends on Java `NetworkInterface`, JNDI DNS exceptions, Hadoop `Time`, platform assumptions, and local `/etc/hosts`/resolver configuration.

## Risks
Highly environment-dependent: reverse DNS, hosts-file contents, Windows behavior, link-local/loopback addresses, and resolver latency can affect tests. `testGetLocalHostIsFast()` uses a broad 20-second threshold to detect caching.

## Test Signals
Signals include non-null local hostname/IP, unknown interface message `No such interface ...`, default IP matching local address, reverse DNS either succeeds or is assumed away, and invalid-DNS fallback returning either a hosts-file result or cached dummy hostname depending on the flag.

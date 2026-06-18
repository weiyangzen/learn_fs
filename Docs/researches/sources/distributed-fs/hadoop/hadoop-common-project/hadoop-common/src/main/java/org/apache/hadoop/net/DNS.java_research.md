<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNS.java

## Purpose
`DNS` provides Hadoop utilities for reverse DNS lookup, network-interface IP discovery, host discovery, and cached local host/address fallbacks.

## Important APIs and Types
Public APIs include `reverseDns`, `getIPs`, `getDefaultIP`, `getHosts`, `getDefaultHost`, `getIPsAsInetAddressList`, and test-visible cached hostname accessors. Static state includes `cachedHostname`, `cachedHostAddress`, and `LOCALHOST`.

## Control Flow
`reverseDns` constructs an IPv4 PTR lookup name, queries JNDI DNS, strips a trailing dot, and returns the host. `getIPs` handles `"default"` by returning the cached address, otherwise resolves a network interface or subinterface and returns ordered addresses, optionally excluding subinterface addresses. `getHosts` reverse-resolves interface addresses, optionally falls back to canonical host names, and finally falls back to the cached hostname. `getDefaultHost` normalizes `"default"` inputs and returns the first host.

## State and Persistence
Local hostname/address are cached statically at class load and can be changed for tests. No external persistence occurs.

## Dependencies and Integration Points
Ganglia sinks and Hadoop daemons use this class for bind/interface host names. It integrates Java `NetworkInterface`, `InetAddress`, JNDI DNS, and shaded Guava `InetAddresses`.

## Risks and Test Signals
`reverseDns` assumes IPv4 dotted decimal addresses and does not support IPv6 PTR construction. Static caches can become stale if host networking changes. Tests should cover default interface fallback, subinterface inclusion/exclusion, reverse DNS trailing dot removal, fallback canonical lookup, cached hostname override, invalid interfaces, and socket exception fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNS.java -->

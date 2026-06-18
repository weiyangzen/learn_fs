# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/MachineList.java

## Purpose

`MachineList` stores hostnames, literal IP addresses, CIDR ranges, or a wildcard and answers whether an `InetAddress` or string address is included.

## Important APIs, Types, And Functions

Constructors accept comma-separated strings or collections and an optional `InetAddressFactory` for tests. `includes(String)` resolves through the factory; `includes(InetAddress)` checks wildcard, exact addresses, then CIDR ranges. `getCollection()` exposes original entries for tests.

## Control Flow, State, And Persistence

Construction copies entries. A single `*` sets `all=true`; otherwise CIDR entries are parsed with `SubnetUtils` using inclusive host counts, and non-CIDR entries are resolved to `InetAddress`. Unknown hosts are logged and skipped. State is immutable sets/lists after construction; no persistence.

## Dependencies And Integration Points

It depends on Apache Commons Net `SubnetUtils`, Java networking, Hadoop `StringUtils`, and SLF4J. `FileBasedIPList` and admission-control code use it for host/IP membership.

## Risks And Test Signals

Hostname resolution happens at construction or string lookup time and can be DNS-dependent. Invalid CIDR syntax throws. Tests should use `InetAddressFactory` to cover wildcard, exact IP, hostname, CIDR, unknown host skipping, null input rejection, and IPv4 range boundaries.

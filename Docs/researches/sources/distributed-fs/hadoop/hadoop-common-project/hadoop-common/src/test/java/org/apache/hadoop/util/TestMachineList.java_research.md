# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestMachineList.java

Purpose: verifies `MachineList`, which matches client machines against wildcard, IP, hostname, CIDR, and mixed allow-list expressions.

Important APIs and types: `MachineList`, `MachineList.InetAddressFactory`, `includes(String)`, `includes(InetAddress)`, `getCollection`, `StringUtils.getTrimmedStringCollection`, and Guava `InetAddresses` through Hadoop's shaded dependency.

Control flow: a fake address factory maps hostnames/IPs deterministically and can simulate unresolved names. Tests cover wildcard matching, raw IP lists with spaces/duplicates, static host collections, hostname reverse/IP matching, CIDR boundaries for /16 and /24 ranges, invalid CIDR rejection, mixed IP/CIDR lists, mixed hostname/IP/CIDR lists, null include arguments, and collection preservation.

State and persistence: all state is in-memory parsed list entries and fake DNS cache mappings. The factory makes PTR-style IP lookups deterministic.

Dependencies and integration points: exercises configuration-style allow-list parsing used by Hadoop services and host/IP security checks.

Risks: DNS resolution variability, CIDR boundary mistakes, duplicate handling, null input exceptions, and loss of original collection entries. Test signals are boundary include/exclude assertions, invalid CIDR exception handling, and collection-size/content checks.

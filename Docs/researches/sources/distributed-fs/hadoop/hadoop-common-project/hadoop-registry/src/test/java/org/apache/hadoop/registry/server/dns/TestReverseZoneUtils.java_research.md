# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestReverseZoneUtils.java

Purpose: unit tests reverse DNS zone address calculations.

Important APIs and functions: tests `ReverseZoneUtils.getReverseZoneNetworkAddress()` and `splitIp()`.

Control flow: assertions cover normal base address calculation, splitting IPv4 octets into long values, negative index rejection, invalid IP rejection, negative range rejection, and several range/index combinations.

State and persistence: pure string/numeric utility tests.

Dependencies and integration: supports `RegistryDNS` split reverse-zone setup and reverse lookup tests.

Risks and test signals: good coverage for arithmetic boundaries and validation. It does not test IPv6 or subnet-mask-derived ranges directly.

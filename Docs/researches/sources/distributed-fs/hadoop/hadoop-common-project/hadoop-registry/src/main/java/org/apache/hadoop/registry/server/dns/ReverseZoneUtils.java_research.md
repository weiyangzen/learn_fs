# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ReverseZoneUtils.java

## Purpose
`ReverseZoneUtils` provides helper calculations for DNS reverse-zone setup, especially when splitting a subnet into multiple reverse zones.

## Important APIs and types
Key methods are `getReverseZoneNetworkAddress(String,int,int)`, `getSubnetCountForReverseZones(Configuration)`, private `calculateIp`, and visible-for-testing `splitIp`. Constants `POW3`, `POW2`, and `POW1` convert IPv4 octets to numeric offsets.

## Control flow
`getSubnetCountForReverseZones` reads subnet, mask, and range from configuration, validates range, computes address count through `SubnetUtils`, and returns either one zone per IP when range is zero or `ipCount / range`. `getReverseZoneNetworkAddress` validates range/index and offsets the base IP by `range * index`.

## State and persistence behavior
The class is stateless. Results are used by `RegistryDNS.addSplitReverseZones()` to create in-memory reverse DNS zones.

## Dependencies and integration points
It depends on Hadoop `Configuration`, Apache Commons Net `SubnetUtils`, Apache Commons Lang `StringUtils`, and DNS registry constants. `RegistryDNS` is the main consumer.

## Risks and test signals
IPv6 is explicitly unsupported. Range handling uses integer division, so non-even subnet/range combinations may leave uncovered addresses. Range zero has special meaning in subnet count but would be invalid for address stepping if used elsewhere. Tests should cover invalid IPs, IPv6 rejection, negative range/index, invalid subnet/mask, range zero, and split calculations across octet boundaries.

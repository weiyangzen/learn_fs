# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ContainerServiceRecordProcessor.java

## Purpose
`ContainerServiceRecordProcessor` converts container-level YARN `ServiceRecord` instances into A, AAAA, PTR, and TXT DNS descriptors.

## Important APIs and types
It extends `BaseServiceRecordProcessor`. Nested descriptors are `TXTContainerRecordDescriptor`, `PTRContainerRecordDescriptor`, `AContainerRecordDescriptor`, and `AAAAContainerRecordDescriptor`. It reads `YarnRegistryAttributes.YARN_IP`, `YARN_HOSTNAME`, `YARN_ID`, and `YARN_COMPONENT`.

## Control flow
`initTypeToInfoMapping()` only proceeds when `yarn:ip` exists. A records target the parsed IP and use names based on container name, container ID, and component name. AAAA records map the same IPv4 address into IPv6. PTR records use reverse IP names when both host and IP exist and point to the container DNS name. TXT records attach the YARN ID to the container name.

## State and persistence behavior
The processor produces transient descriptors that are later registered or removed from in-memory DNS zones. It does not persist to ZooKeeper.

## Dependencies and integration points
It depends on YARN service-record attributes, registry path parsing in the base class, xbill DNS types, and Java networking. `RegistryDNS` chooses it when `yarn:persistence` equals `container`.

## Risks and test signals
Several descriptor init methods catch parse exceptions with TODO-style comments and may leave null names, which can later fail during record creation or zone selection. Missing `yarn:ip` silently produces no descriptors. Tests should cover full container records, missing host/IP/component/description cases, PTR generation, null-name behavior, and record removal symmetry.

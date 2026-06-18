# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/ProtocolTypes.java

## Purpose
`ProtocolTypes` defines common protocol strings for endpoint metadata in service records.

## Important APIs and types
Constants include Hadoop filesystem, Hadoop IPC, IIOP, REST, RMI, Sun RPC, Thrift, TCP, UDP, unknown, web UI, web services, and ZooKeeper binding protocol names.

## Control flow
There are no methods. Values are assigned to `Endpoint.protocolType` by publishers and interpreted by clients according to application conventions.

## State and persistence behavior
Protocol strings are persisted as JSON and form part of the registry service-record contract. Unknown or custom values are represented by strings, with `PROTOCOL_UNKNOWN` as the empty string.

## Dependencies and integration points
It integrates with `Endpoint`, `ServiceRecord`, and client code that resolves endpoint protocol choices. DNS code in this subset focuses more on address type and API name than protocol type.

## Risks and test signals
Because protocols are plain strings, registry validation must allow custom protocols while still rejecting null fields. Tests should verify standard constants survive JSON round trips and that unknown protocols are accepted where the data model promises extensibility.

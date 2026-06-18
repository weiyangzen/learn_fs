# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/AddressTypes.java

## Purpose
`AddressTypes` defines string constants for endpoint address encodings used in JSON service records. Strings are used instead of Java enums for cross-language serialization compatibility.

## Important APIs and types
Important address type constants are `ADDRESS_HOSTNAME_AND_PORT`, `ADDRESS_PATH`, `ADDRESS_URI`, `ADDRESS_ZOOKEEPER`, and `ADDRESS_OTHER`. Field names include `ADDRESS_HOSTNAME_FIELD` and `ADDRESS_PORT_FIELD`.

## Control flow
There is no control flow. Constructors and processors in `Endpoint`, `RegistryTypeUtils`, and DNS service-record processors interpret these strings.

## State and persistence behavior
Values become persisted JSON fields in `Endpoint.addressType` and keys in endpoint address maps. They form part of the external registry data contract.

## Dependencies and integration points
`Endpoint` uses these constants when constructing URI endpoints. `BaseServiceRecordProcessor` interprets `host/port` and `uri` endpoints to extract host, port, and TXT path values. Clients publishing service records must use the same names.

## Risks and test signals
Because address payloads are maps of strings, malformed or missing keys fail later in processors rather than at deserialization. Tests should cover all standard address types, especially DNS extraction from `host/port` and `uri`.

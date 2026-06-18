# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/Endpoint.java

## Purpose
`Endpoint` is the JSON-marshallable description of one service or component API endpoint. It records the API identifier, address encoding, protocol, and one or more address maps.

## Important APIs and types
Public fields are `api`, `addressType`, `protocolType`, and `addresses`. Constructors support empty creation for Jackson, deep-copy construction, explicit address lists, a single address map, varargs address maps, and URI varargs. `validate()` checks required fields and non-null address entries. `toString()` delegates to a static `JsonSerDeser<Endpoint>` marshal.

## Control flow
The deep-copy constructor clones the address list and maps. URI construction sets `addressType` to `AddressTypes.ADDRESS_URI` and creates address maps through `RegistryTypeUtils.uri`. `validate()` is called by `ServiceRecord.addExternalEndpoint`, `addInternalEndpoint`, and higher-level service-record validation before persistence.

## State and persistence behavior
Instances are mutable DTOs intended for JSON persistence inside `ServiceRecord`. The copy constructor is deep for addresses, while `clone()` is explicitly shallow and shares address list objects.

## Dependencies and integration points
It depends on Jackson annotations, Hadoop `Preconditions`, `JsonSerDeser`, `RegistryTypeUtils`, `AddressTypes`, and `ProtocolTypes`. DNS processors consume endpoint address maps to generate A, AAAA, CNAME, SRV, and TXT records.

## Risks and test signals
The public mutable fields are convenient for JSON but can be changed after validation. `clone()` is shallow while the copy constructor is deep, so tests should distinguish them. DNS code assumes at least one address and specific keys for selected address types; endpoint validation does not enforce address schema by type, so schema-specific tests belong in registry type utilities and DNS processors.

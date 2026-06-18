# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/ServiceRecord.java

## Purpose
`ServiceRecord` is the primary JSON-marshallable registry value describing a service/component, its attributes, and internal/external endpoints.

## Important APIs and types
Public fields are `type`, `description`, `external`, and `internal`; unknown JSON attributes are stored in private `attributes`. `RECORD_TYPE` identifies valid registry records. Methods add and retrieve endpoints, set and get attributes with Jackson `@JsonAnySetter`/`@JsonAnyGetter`, find endpoints by API, render to string, and implement equality/hashCode. The copy constructor deep-copies attributes and endpoints.

## Control flow
Publishers populate attributes and endpoints, `addExternalEndpoint`/`addInternalEndpoint` validate endpoints immediately, and `RegistryOperationsService.bind()` invokes registry-wide validation before marshalling. DNS processors read YARN attributes and endpoint lists to generate records.

## State and persistence behavior
Instances are mutable DTOs stored as JSON bytes in ZooKeeper. Unknown JSON fields are retained in `attributes` and emitted through `@JsonAnyGetter`; the class comments say generated JSON does not include creation of unknown attributes, but the getter exposes the map during serialization.

## Dependencies and integration points
It depends on Jackson any-getter/setter support, Hadoop `Preconditions`, and `Endpoint`. YARN-specific constants in `YarnRegistryAttributes` define expected attribute keys. `RegistryUtils.ServiceRecordMarshal` serializes/deserializes it, and DNS processors require `yarn:persistence`, `yarn:ip`, `yarn:hostname`, `yarn:id`, and component data.

## Risks and test signals
`findByAPI` assumes endpoints are non-null and have non-null APIs. `set(String,Object)` calls `toString()` on values, so null unknown attributes would fail. `clone()` is shallow despite a deep-copy constructor. Tests should cover JSON round trips, unknown attribute preservation, endpoint validation, equality including endpoints/attributes, and DNS behavior for missing YARN attributes.

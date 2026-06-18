# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/package-info.java

## Purpose
This package descriptor documents the JSON data model saved to or derived from the registry.

## Important APIs and types
It identifies `ServiceRecord` and `Endpoint` as the core persisted data types and `AddressTypes`, `PersistencePolicies`, and `ProtocolTypes` as supporting field-value contracts. It also explains that `RegistryPathStatus` is a status object, not a saved service record.

## Control flow
There is no executable control flow. The descriptor guides how clients should view the package boundary.

## State and persistence behavior
The package's data types are designed for JSON marshalling into ZooKeeper registry entries. `RegistryPathStatus` is transient metadata that can still be serialized.

## Dependencies and integration points
These types are consumed by registry clients, YARN publishers, registry admin cleanup selectors, and DNS record processors.

## Risks and test signals
Package-level docs signal that cross-language JSON compatibility is a design goal. Tests should favor stable field names and string constants over Java-only enum assumptions.

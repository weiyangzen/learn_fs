# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/RegistryPathStatus.java

## Purpose
`RegistryPathStatus` is the JSON-friendly result of a registry `stat()` call. It summarizes one registry entry's name, timestamp, data size, and child count.

## Important APIs and types
The final fields are `path`, `time`, `size`, and `children`, populated through a Jackson `@JsonProperty` constructor. `equals()` compares path, time, and size but intentionally ignores `children`; `hashCode()` derives only from path.

## Control flow
Instances are created by `RegistryOperationsService.stat()` from ZooKeeper `Stat`, using the last path entry as `path`, creation time as `time`, data length as `size`, and number of children as `children`.

## State and persistence behavior
This class is not stored in the registry as service data; it is a status DTO that can be serialized for APIs or REST front ends. It reflects ZooKeeper metadata at one point in time.

## Dependencies and integration points
It uses Jackson annotations and Hadoop audience/stability annotations. It is consumed by registry listing/extraction utilities and by `SelectByYarnPersistence` selectors, though selectors in this subset do not inspect its fields.

## Risks and test signals
Ignoring `children` in equality but including it in `toString()` is intentional but can surprise caches or comparisons. Tests should assert JSON construction, equality semantics, and `RegistryOperationsService.stat()` mapping.

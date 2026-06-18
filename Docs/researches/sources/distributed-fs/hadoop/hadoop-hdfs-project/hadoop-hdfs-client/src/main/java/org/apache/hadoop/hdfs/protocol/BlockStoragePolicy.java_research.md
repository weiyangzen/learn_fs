# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockStoragePolicy.java

## Purpose
`BlockStoragePolicy` describes preferred and fallback storage media for block replicas, including creation fallback, replication fallback, and copy-on-create policy behavior.

## Important APIs, types, and functions
Constructors set a 4-bit id, name, preferred `StorageType[]`, creation fallbacks, replication fallbacks, and optional `copyOnCreateFile`. `chooseStorageTypes(short)` returns desired non-transient storage types for a replication factor. Overloads subtract already chosen types and handle unavailable storage by replacing with creation or replication fallbacks. `chooseExcess` identifies storage types to delete. `getCreationFallback`, `getReplicationFallback`, `equals`, `hashCode`, `toString`, and `BlockStoragePolicySpi` getters expose policy metadata.

## Control flow
Storage selection starts from preferred types, skips transient types for usage-accounting accuracy, repeats the last non-transient type if more replicas are needed, subtracts already chosen types with `diff`, replaces unavailable types from the appropriate fallback list, removes excess after fallback replacement, and logs if not enough storage types remain to satisfy expected replicas.

## State and persistence behavior
State is policy metadata and arrays. The only mutable field is `copyOnCreateFile`, though it is set only by constructors. Equality and hash use policy id only, making id uniqueness critical.

## Dependencies and integration points
It implements `BlockStoragePolicySpi` and depends on `StorageType`, `EnumSet`, and logging. It is used by NameNode/block placement and exposed through filesystem storage policy APIs.

## Risks and test signals
Tests should cover transient storage exclusion, replication larger than preferred list, chosen/excess subtraction with duplicates, fallback selection for new blocks versus replication, unavailable fallback exhaustion warnings, equality by id, copy-on-create flag, and array mutation risks through returned arrays.

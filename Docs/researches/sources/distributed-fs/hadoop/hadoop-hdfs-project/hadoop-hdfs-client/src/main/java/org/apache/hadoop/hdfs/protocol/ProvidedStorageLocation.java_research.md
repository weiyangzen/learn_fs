# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ProvidedStorageLocation.java

## Purpose
`ProvidedStorageLocation` identifies data for a block replica located in an external/provided storage system. It carries a `Path`, byte offset, length, and nonce.

## APIs and Behavior
The constructor stores path, offset, length, and a defensive copy of nonce. Getters expose path, offset, length, and a fresh copy of nonce. Equality and hash code include all fields and array contents.

## State, Dependencies, and Integration
The object is immutable if the `Path` is treated as immutable. It integrates with provided-storage block mapping and `LocatedBlock` behavior that moves `StorageType.PROVIDED` locations after normal replicas.

## Risks and Test Signals
The constructor assumes `nonce` is non-null. There is no validation for negative offsets/lengths. Tests should cover nonce defensive copies, equality/hash behavior, null nonce failure, external path identity, and read behavior for provided-storage replicas.

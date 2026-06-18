# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSServerJSONUtils.java

## Purpose
`KMSServerJSONUtils.java` converts server-side `KeyProvider` metadata and key-version collections into REST-compatible JSON maps/lists.

## Important APIs, Types, and Functions
`toJSON(List<KeyProvider.KeyVersion>)` maps each key version through `KMSUtil.toJSON`. `toJSON(String, Metadata)` emits name, cipher, length, description, attributes, created timestamp, and version count. `toJSON(String[], Metadata[])` pairs names with metadata arrays.

## Control Flow
`KMS.java` calls these helpers for metadata, metadata batches, and key version lists. Null metadata returns an empty map for that key rather than an error.

## State and Persistence
The class is stateless and creates new list/map objects for responses.

## Dependencies and Integration Points
It depends on `KMSRESTConstants`, `KMSUtil`, and `KeyProvider`. Output is serialized by `KMSJSONWriter`.

## Risks
The batch converter assumes `keyNames` and `metas` have matching lengths. Null metadata producing `{}` may be a compatibility contract clients rely on, but it can also hide missing keys if callers do not validate.

## Test Signals
Tests should verify field names and types, null metadata behavior, ordering in batch responses, and key version conversion compatibility.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/Event.java

## Purpose
`Event` defines the public unstable data model emitted by HDFS inotify. It represents edit-log-derived filesystem changes such as create, close, append, rename, metadata update, unlink, and truncate.

## Important APIs, types, and functions
The base class stores an `EventType` enum. Nested event classes include `CloseEvent`, `CreateEvent`, `MetadataUpdateEvent`, `RenameEvent`, `AppendEvent`, `UnlinkEvent`, and `TruncateEvent`. `CreateEvent` has an `INodeType` enum and builder for file/directory/symlink creation fields including owner, group, permissions, symlink target, overwrite flag, default block size, and optional erasure-coded flag. `MetadataUpdateEvent` has `MetadataType` values for times, replication, owner, permissions, ACLs, and xAttrs, also using a builder. Rename, append, and unlink use builders; close and truncate use direct constructors.

## Control flow
There is little behavior beyond construction, getters, and `toString`. Builders accumulate optional fields and create immutable-in-practice event instances. `MetadataUpdateEvent.toString` conditionally includes fields based on `metadataType`. Create string formatting conditionally includes symlink target.

## State and persistence behavior
Each event instance stores event payload fields in memory. Lists for ACLs and xAttrs are referenced directly rather than defensively copied. There is no persistence here; events are serialized/deserialized elsewhere from edit-log/inotify RPC data.

## Dependencies and integration points
It depends on Hadoop permissions (`FsPermission`, `AclEntry`), `XAttr`, Java `Optional`, and classification annotations. It is consumed by HDFS inotify streams and event batches, exposing user-visible event metadata.

## Risks and test signals
Tests should cover every event type, builder field propagation, optional erasure-coded absence/presence, symlink-only target semantics, metadata-specific `toString`, ACL/xAttr null handling, timestamp/file-size getters, and public unstable compatibility. Because fields are mutable references and not final, callers should not assume deep immutability of ACL/xAttr lists.

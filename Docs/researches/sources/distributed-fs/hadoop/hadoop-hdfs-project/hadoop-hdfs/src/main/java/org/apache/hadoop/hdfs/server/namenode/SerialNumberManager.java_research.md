# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SerialNumberManager.java

## Purpose

`SerialNumberManager.java` manages shared string-to-integer tables for compact on-disk and in-memory metadata encodings, especially user, group, ACL entry names, and xattr names. The source was read as a complete 162-line file.

## Important APIs, Types, and Functions

The enum constants are `GLOBAL`, `USER`, `GROUP`, and `XATTR`. Each owns a `SerialNumberMap<String>` and a bit length derived from the fields that embed its IDs. Public methods include `getSerialNumber`, `getString`, `getString(int, StringTable)`, `getStringTable`, and `newStringTable`. The nested `StringTable` stores packed IDs to strings and exposes `put`, `iterator`, `size`, and `getMaskBits`.

## Control Flow

Static initialization computes how many high-order mask bits are needed to distinguish manager namespaces in a saved string table, narrows each manager's usable ID bit length, creates the maps, and logs their capacity. Runtime calls allocate serial numbers lazily through `SerialNumberMap`. Saving creates a snapshot `StringTable` by OR-ing manager-specific high bits into each entry ID. Loading creates an empty table with an expected size and mask width, then lookup re-applies the current manager mask when needed.

## State and Persistence Behavior

The enum instances hold process-wide maps that grow as metadata strings are encountered. `StringTable` is the persistence bridge for fsimage serialization: it snapshots string mappings so compact IDs in inodes, ACLs, and xattrs can be decoded during image load. ID `0` is reserved for null by the underlying map.

## Dependencies and Integration Points

The bit lengths are constrained by `PermissionStatusFormat.USER`, `PermissionStatusFormat.GROUP`, `AclEntryStatusFormat.NAME`, and `XAttrFormat.NAME`, all using `LongBitFormat.Enum`. `FSImage` serialization/deserialization consumes the string table when persisting compact metadata.

## Risks and Edge Cases

Capacity is finite and based on bit allocation; exceeding a map's maximum throws. String table mask bits must not exceed the current supported mask width or loading fails. Persisted IDs are only meaningful with the matching string table, so incorrect table reconstruction can misattribute owners, groups, ACL names, or xattr names.

## Test Signals

Tests should cover null ID behavior, lazy allocation stability, save/load `StringTable` masking for all managers, rejection of excessive mask bits, capacity overflow, lookup of missing IDs, and fsimage round trips with users, groups, ACL names, and xattr names.

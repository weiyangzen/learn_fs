# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrFeature.java

## Purpose

`XAttrFeature.java` stores extended attributes as an `INode.Feature`, optimizing small xattrs into a packed byte array while keeping large values in an immutable list. The source was read as a complete 122-line file.

## Important APIs, Types, and Functions

The class defines `PACK_THRESHOLD` of 1024 bytes, fields `attrs` and `xAttrs`, constructor, `getXAttrs`, `getXAttr`, `equals`, and `hashCode`.

## Control Flow

Construction partitions input xattrs: null values and values up to the threshold are packed with `XAttrFormat.toBytes`, while larger values are stored in an `ImmutableList`. `getXAttrs` unpacks the byte array and appends large xattrs if present. `getXAttr` first searches packed bytes by prefixed name, then scans large xattrs using `equalsIgnoreValue`.

## State and Persistence Behavior

The feature is attached to inodes and may be captured by snapshot inode attributes. Packed bytes use `XAttrFormat`, which is both in-memory and on-disk format. Large xattrs are immutable in memory but still serialized by higher-level fsimage code.

## Dependencies and Integration Points

It integrates with `INode.Feature`, `XAttrFormat`, `XAttrHelper`, Guava `ImmutableList`, and `XAttrStorage`. NameNode xattr operations build and replace this feature under directory locks.

## Risks and Edge Cases

The 1024-byte threshold affects memory layout and lookup cost. Equality reconstructs lists and hashes array copies, which is acceptable for metadata comparison but not free. Any incompatible change to `XAttrFormat` would affect this feature's persisted packed state.

## Test Signals

Tests should cover empty/null input, small-only, large-only, mixed ordering, exact threshold behavior, lookup by prefixed name, no-value xattrs, equality/hash consistency, and fsimage/snapshot round trips.

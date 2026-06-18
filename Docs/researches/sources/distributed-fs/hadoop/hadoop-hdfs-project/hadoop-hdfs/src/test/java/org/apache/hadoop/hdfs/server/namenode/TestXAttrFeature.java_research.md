# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestXAttrFeature.java

## Purpose

`TestXAttrFeature` verifies in-memory `XAttrFeature` lookup and listing across several XAttr namespaces, empty values, large values, and missing keys.

## Important APIs, Types, and Functions

The test builds `XAttr` instances through `XAttrHelper.buildXAttr`, creates `XAttrFeature` from a mutable list, and calls `getXAttr` and `getXAttrs`. Static data covers `system`, `security`, `trusted`, `user`, and `raw` prefixes plus random 1800- and 2000-byte values and a deterministic 128-byte value.

## Control Flow

The test first asserts an empty feature returns an empty list. It then creates a feature with one XAttr and verifies direct lookup and size. It adds several more XAttrs, recreates the feature, verifies each lookup returns an equal XAttr, verifies the returned list size matches input, confirms every returned item was supplied, and confirms a missing key returns null.

## State and Persistence Behavior

All state is in-memory feature data. It indirectly covers metadata representation that can be serialized in fsimage/edit logs elsewhere.

## Dependencies and Integration Points

This unit test covers the NameNode inode XAttr feature object used by namespace metadata and depends on helper parsing of prefixed XAttr names.

## Risks and Edge Cases

Large XAttr values can stress packing/storage behavior. A feature implementation that drops namespace distinctions, value-less XAttrs, raw namespace entries, or large values would fail lookups.

## Test Signals

Signals include empty-list behavior, equality of every retrieved XAttr, returned list size equal to source list size, membership preservation, and null for `user.a8`.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrFormat.java

## Purpose

`XAttrFormat.java` defines the compact binary encoding for HDFS xattrs used both in memory and on disk. The source was read as a complete 195-line file.

## Important APIs, Types, and Functions

The enum fields are `RESERVED`, `NS_EXT`, `NAME`, and `NS`, each backed by `LongBitFormat`. Important methods are `getNamespace`, `getName`, `toInt`, `toXAttr`, `toXAttrs`, `getXAttr`, and `toBytes`. `XATTR_VALUE_LEN_MAX` caps values to less than 64 KiB in packed form.

## Control Flow

`toInt` allocates or retrieves a serial number for the xattr name and combines namespace low bits, namespace extension bits, and name ID into an integer record. `toBytes` emits for each xattr a big-endian 4-byte record, 2-byte unsigned value length, and optional value bytes. `toXAttrs` scans a byte array sequentially and reconstructs builders. `getXAttr` avoids unpacking all entries by comparing namespace and name while scanning.

## State and Persistence Behavior

This format is explicitly persistent and incompatible if changed. Name strings are persisted indirectly through `SerialNumberManager.XATTR` and fsimage string tables. Packed bytes are embedded in `XAttrFeature`.

## Dependencies and Integration Points

It integrates with `XAttr`, `XAttrHelper`, `SerialNumberManager`, Guava `Ints`, and `LongBitFormat`. FSImage load uses `toXAttr(record, value, stringTable)` to resolve historical string table IDs.

## Risks and Edge Cases

Malformed byte arrays can cause index errors because parsing assumes well-formed storage. Value length must fit in 16 bits; larger packed values are rejected and should be handled by `XAttrFeature` as large list entries. Namespace ordinal encoding depends on `XAttr.NameSpace` ordering.

## Test Signals

Tests should cover byte-level round trips, all namespaces including extended namespace bits, null and zero-length values, oversized value rejection, lookup by prefixed name, string table decoding, malformed/truncated bytes, and compatibility with existing fsimage fixtures.

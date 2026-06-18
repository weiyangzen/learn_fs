# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeID.java

## Purpose
`DatanodeID` is the primary identity/contact descriptor for a DataNode. It combines IP address, host name, peer host name, data-transfer/IPC/info ports, transfer address cache, and the DataNode UUID used to identify the node across registrations and block ownership.

## APIs and Behavior
Constructors copy from another `DatanodeID` or accept explicit network fields. The class caches UTF-8 `ByteString` forms for protobuf serde and caches `xferAddr` after `setIpAndXferPort`. Public accessors expose IP, host, peer host, transfer, info, secure info, and IPC addresses, with hostname/IP selection helpers. `updateRegInfo()` updates contact fields from a new registration but intentionally does not update the UUID. `compareTo()` orders by transfer address.

## State, Dependencies, and Integration
The object is mutable for registration contact fields but immutable for `datanodeUuid`. It integrates with protobuf through `ByteString`, client/network code through `InetSocketAddress`, and `DatanodeInfo`, which extends it. Equality requires both transfer address equality and UUID equality; hash code is based on UUID.

## Risks and Test Signals
`checkDatanodeUuid()` normalizes null/empty UUID to `null`, but `equals()` and `hashCode()` dereference `datanodeUuid`, so placeholder or not-yet-assigned IDs can throw if used in hashed collections. Tests should cover registration updates, hostname/IP address formatting, UUID preservation, byte-string cache consistency, equality/hash behavior with null UUIDs, and sorted ordering by transfer address.

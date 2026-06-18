# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/proto/xattr.proto

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/proto/xattr.proto` is a Hadoop HDFS protobuf schema read as a complete 75-line source file. It defines protobuf representation of HDFS extended attributes and xattr RPC payloads. The header marks these private/stable wire contracts where field numbers, required/optional status, and generated Java names are compatibility-sensitive.

## Important APIs, Types, and Functions

Major declared protobuf types include `XAttrProto`, `XAttrSetFlagProto`, `SetXAttrRequestProto`, `SetXAttrResponseProto`, `GetXAttrsRequestProto`, `GetXAttrsResponseProto`, `ListXAttrsRequestProto`, `ListXAttrsResponseProto`, `RemoveXAttrRequestProto`, `RemoveXAttrResponseProto`. RPCs declared in this file include none declared locally. The schema `XAttrProto` with namespace/name/optional value, `XAttrSetFlagProto`, and set/get/list/remove request/response messages.

## Control Flow

There is no direct runtime control flow in the `.proto` file. Build tooling generates Java message and service classes, client translators populate request messages, server-side translators unpack them into HDFS domain objects, and responses are serialized back over Hadoop RPC or the DataTransfer stream path.

## State and Persistence Behavior

The file defines wire state rather than owning runtime storage. Required fields must be present on the wire, optional fields model feature evolution or nullable server results, repeated fields carry listings/status collections, and cursor fields support batched APIs. Some messages represent durable HDFS metadata such as blocks, quotas, snapshots, ACLs, xattrs, encryption zones, and erasure coding policies, but persistence is owned by NameNode/DataNode code outside the schema.

## Dependencies and Integration Points

Proto imports: none declared locally. integrates with ClientNamenodeProtocol xattr RPCs and Java xattr converters; set flags are encoded as bit values. The generated Java classes are consumed by HDFS protobuf translators, client protocol proxies, NameNode RPC implementations, DataNode protocol handlers, and compatibility tests.

## Risks and Edge Cases

The largest risk is wire incompatibility: reusing field numbers, changing required fields, renaming generated service methods, or changing enum numeric values can break rolling upgrades and mixed-version clients. Required fields make omission fatal, while optional fields require translators to preserve old-client behavior. Large repeated responses also need batching/cursor handling to avoid memory pressure.

## Test Signals

Coverage should include protobuf translator round trips, old/new client compatibility, missing optional field behavior, enum numeric stability, batched-listing cursor behavior, and integration tests for the corresponding HDFS RPC or DataTransfer operation.

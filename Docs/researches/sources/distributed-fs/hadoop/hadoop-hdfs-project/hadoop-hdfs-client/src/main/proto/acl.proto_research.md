# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/proto/acl.proto

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/proto/acl.proto` is a Hadoop HDFS protobuf schema read as a complete 113-line source file. It defines protobuf representation of HDFS ACLs and ACL RPC payloads. The header marks these private/stable wire contracts where field numbers, required/optional status, and generated Java names are compatibility-sensitive.

## Important APIs, Types, and Functions

Major declared protobuf types include `FsPermissionProto`, `AclEntryProto`, `AclStatusProto`, `ModifyAclEntriesRequestProto`, `ModifyAclEntriesResponseProto`, `RemoveAclRequestProto`, `RemoveAclResponseProto`, `RemoveAclEntriesRequestProto`, `RemoveAclEntriesResponseProto`, `RemoveDefaultAclRequestProto`, `RemoveDefaultAclResponseProto`, `SetAclRequestProto`, `SetAclResponseProto`, `GetAclStatusRequestProto`, `GetAclStatusResponseProto`. RPCs declared in this file include none declared locally. The schema `FsPermissionProto`, `AclEntryProto` with scope/type/action enums, `AclStatusProto`, and request/response messages for modify, remove, remove entries, remove default, set, and get ACL status.

## Control Flow

There is no direct runtime control flow in the `.proto` file. Build tooling generates Java message and service classes, client translators populate request messages, server-side translators unpack them into HDFS domain objects, and responses are serialized back over Hadoop RPC or the DataTransfer stream path.

## State and Persistence Behavior

The file defines wire state rather than owning runtime storage. Required fields must be present on the wire, optional fields model feature evolution or nullable server results, repeated fields carry listings/status collections, and cursor fields support batched APIs. Some messages represent durable HDFS metadata such as blocks, quotas, snapshots, ACLs, xattrs, encryption zones, and erasure coding policies, but persistence is owned by NameNode/DataNode code outside the schema.

## Dependencies and Integration Points

Proto imports: none declared locally. integrates with `ClientNamenodeProtocol.proto` and Java ACL translators; permission is stored as a uint32 even though only short-width bits are used. The generated Java classes are consumed by HDFS protobuf translators, client protocol proxies, NameNode RPC implementations, DataNode protocol handlers, and compatibility tests.

## Risks and Edge Cases

The largest risk is wire incompatibility: reusing field numbers, changing required fields, renaming generated service methods, or changing enum numeric values can break rolling upgrades and mixed-version clients. Required fields make omission fatal, while optional fields require translators to preserve old-client behavior. Large repeated responses also need batching/cursor handling to avoid memory pressure.

## Test Signals

Coverage should include protobuf translator round trips, old/new client compatibility, missing optional field behavior, enum numeric stability, batched-listing cursor behavior, and integration tests for the corresponding HDFS RPC or DataTransfer operation.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/proto/ClientNamenodeProtocol.proto

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/proto/ClientNamenodeProtocol.proto` is a Hadoop HDFS protobuf schema read as a complete 1094-line source file. It defines main private stable protobuf RPC contract for the HDFS `ClientProtocol` NameNode API. The header marks these private/stable wire contracts where field numbers, required/optional status, and generated Java names are compatibility-sensitive.

## Important APIs, Types, and Functions

Major declared protobuf types include `GetBlockLocationsRequestProto`, `GetBlockLocationsResponseProto`, `GetServerDefaultsRequestProto`, `GetServerDefaultsResponseProto`, `CreateFlagProto`, `CreateRequestProto`, `CreateResponseProto`, `AppendRequestProto`, `AppendResponseProto`, `SetReplicationRequestProto`, `SetReplicationResponseProto`, `SetStoragePolicyRequestProto`, `SetStoragePolicyResponseProto`, `UnsetStoragePolicyRequestProto`, `UnsetStoragePolicyResponseProto`, `GetStoragePolicyRequestProto`, `GetStoragePolicyResponseProto`, `GetStoragePoliciesRequestProto`, `GetStoragePoliciesResponseProto`, `SetPermissionRequestProto`, `SetPermissionResponseProto`, `SetOwnerRequestProto`, `SetOwnerResponseProto`, `AbandonBlockRequestProto`, `AbandonBlockResponseProto`, `AddBlockFlagProto`, `AddBlockRequestProto`, `AddBlockResponseProto`, `GetAdditionalDatanodeRequestProto`, `GetAdditionalDatanodeResponseProto`, and 154 more. RPCs declared in this file include `getBlockLocations`, `getServerDefaults`, `create`, `append`, `setReplication`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, `getStoragePolicies`, `setPermission`, `setOwner`, `abandonBlock`, `addBlock`, `getAdditionalDatanode`, `complete`, `reportBadBlocks`, `concat`, `truncate`, `rename`, `rename2`, `delete`, `mkdirs`, `getListing`, `getBatchedListing`, `renewLease`, `recoverLease`, `getFsStats`, `getFsReplicatedBlockStats`, `getFsECBlockGroupStats`, `getDatanodeReport`, `getDatanodeStorageReport`, `getPreferredBlockSize`, `setSafeMode`, `saveNamespace`, `rollEdits`, and 76 more. The schema defines request/response messages and `ClientNamenodeProtocol` RPCs for block locations, create/append/complete, block allocation, rename/delete/mkdir/listing, lease renewal/recovery, cluster stats, datanode reports, safe mode/admin operations, rolling upgrade, cache directives/pools, symlinks, pipeline recovery, delegation tokens, encryption zones, snapshots, ACLs, xattrs, erasure coding, quotas, edit-log tailing, open-file listing, msync, storage policy satisfaction, HA state, slow datanode reports, and enclosing-root lookup.

## Control Flow

There is no direct runtime control flow in the `.proto` file. Build tooling generates Java message and service classes, client translators populate request messages, server-side translators unpack them into HDFS domain objects, and responses are serialized back over Hadoop RPC or the DataTransfer stream path.

## State and Persistence Behavior

The file defines wire state rather than owning runtime storage. Required fields must be present on the wire, optional fields model feature evolution or nullable server results, repeated fields carry listings/status collections, and cursor fields support batched APIs. Some messages represent durable HDFS metadata such as blocks, quotas, snapshots, ACLs, xattrs, encryption zones, and erasure coding policies, but persistence is owned by NameNode/DataNode code outside the schema.

## Dependencies and Integration Points

Proto imports: `Security.proto`, `hdfs.proto`, `acl.proto`, `xattr.proto`, `encryption.proto`, `inotify.proto`, `erasurecoding.proto`, `HAServiceProtocol.proto`. imports security, ACL, xattr, encryption, erasure-coding, and shared HDFS protos; generated Java is the wire bridge used by protobuf translators on both client and NameNode sides. The generated Java classes are consumed by HDFS protobuf translators, client protocol proxies, NameNode RPC implementations, DataNode protocol handlers, and compatibility tests.

## Risks and Edge Cases

The largest risk is wire incompatibility: reusing field numbers, changing required fields, renaming generated service methods, or changing enum numeric values can break rolling upgrades and mixed-version clients. Required fields make omission fatal, while optional fields require translators to preserve old-client behavior. Large repeated responses also need batching/cursor handling to avoid memory pressure.

## Test Signals

Coverage should include protobuf translator round trips, old/new client compatibility, missing optional field behavior, enum numeric stability, batched-listing cursor behavior, and integration tests for the corresponding HDFS RPC or DataTransfer operation.

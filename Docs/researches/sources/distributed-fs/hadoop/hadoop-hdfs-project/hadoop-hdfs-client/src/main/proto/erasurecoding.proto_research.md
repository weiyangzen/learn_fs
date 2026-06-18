# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/proto/erasurecoding.proto

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/proto/erasurecoding.proto` is a Hadoop HDFS protobuf schema read as a complete 120-line source file. It defines protobuf payloads for HDFS erasure coding policy administration. The header marks these private/stable wire contracts where field numbers, required/optional status, and generated Java names are compatibility-sensitive.

## Important APIs, Types, and Functions

Major declared protobuf types include `SetErasureCodingPolicyRequestProto`, `SetErasureCodingPolicyResponseProto`, `GetErasureCodingPoliciesRequestProto`, `GetErasureCodingPoliciesResponseProto`, `GetErasureCodingCodecsRequestProto`, `GetErasureCodingCodecsResponseProto`, `GetErasureCodingPolicyRequestProto`, `GetErasureCodingPolicyResponseProto`, `AddErasureCodingPoliciesRequestProto`, `AddErasureCodingPoliciesResponseProto`, `RemoveErasureCodingPolicyRequestProto`, `RemoveErasureCodingPolicyResponseProto`, `EnableErasureCodingPolicyRequestProto`, `EnableErasureCodingPolicyResponseProto`, `DisableErasureCodingPolicyRequestProto`, `DisableErasureCodingPolicyResponseProto`, `UnsetErasureCodingPolicyRequestProto`, `UnsetErasureCodingPolicyResponseProto`, `GetECTopologyResultForPoliciesRequestProto`, `GetECTopologyResultForPoliciesResponseProto`, `BlockECReconstructionInfoProto`, `CodecProto`. RPCs declared in this file include none declared locally. The schema messages cover set/unset/get policy, list policies/codecs, add/remove/enable/disable policies, topology verification, and codec property maps.

## Control Flow

There is no direct runtime control flow in the `.proto` file. Build tooling generates Java message and service classes, client translators populate request messages, server-side translators unpack them into HDFS domain objects, and responses are serialized back over Hadoop RPC or the DataTransfer stream path.

## State and Persistence Behavior

The file defines wire state rather than owning runtime storage. Required fields must be present on the wire, optional fields model feature evolution or nullable server results, repeated fields carry listings/status collections, and cursor fields support batched APIs. Some messages represent durable HDFS metadata such as blocks, quotas, snapshots, ACLs, xattrs, encryption zones, and erasure coding policies, but persistence is owned by NameNode/DataNode code outside the schema.

## Dependencies and Integration Points

Proto imports: `hdfs.proto`. imports `hdfs.proto` for `ErasureCodingPolicyProto` and related response/status structures; it is used by ClientNamenodeProtocol EC RPCs. The generated Java classes are consumed by HDFS protobuf translators, client protocol proxies, NameNode RPC implementations, DataNode protocol handlers, and compatibility tests.

## Risks and Edge Cases

The largest risk is wire incompatibility: reusing field numbers, changing required fields, renaming generated service methods, or changing enum numeric values can break rolling upgrades and mixed-version clients. Required fields make omission fatal, while optional fields require translators to preserve old-client behavior. Large repeated responses also need batching/cursor handling to avoid memory pressure.

## Test Signals

Coverage should include protobuf translator round trips, old/new client compatibility, missing optional field behavior, enum numeric stability, batched-listing cursor behavior, and integration tests for the corresponding HDFS RPC or DataTransfer operation.

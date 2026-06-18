# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/RpcSensitiveConfigMaskTest.java

## Purpose
`RpcSensitiveConfigMaskTest` verifies that RPC debug/log masking hides sensitive UFS configuration values inside several protobuf request/response shapes.

## Important APIs, Types, and Functions
The test `maskObjectsAll()` exercises `RpcSensitiveConfigMask.CREDENTIAL_FIELD_MASKER.maskObjects()`, `MountPOptions`, `MountPRequest`, `UfsInfo`, `GetUfsInfoPResponse`, `UpdateMountPRequest`, and sensitive key `PropertyKey.Name.S3A_ACCESS_KEY`.

## Control Flow, State, and Persistence
The test constructs different protobuf objects containing a normal key/value and an S3 access key with value `mycredential`, stringifies the masked output, and asserts that normal data and key names remain visible while the credential value is absent and `Masked` appears. It also verifies a plain string is left unmasked. There is no persistence.

## Dependencies and Integration Points
It depends on generated gRPC/protobuf classes and the sensitive-config masker used for RPC logging or diagnostics.

## Risks and Test Signals
Risks covered include credential leakage from nested properties builders and accidental masking of non-protobuf objects. Passing tests signal coverage for common mount and UFS info RPC types, though new protobuf shapes need explicit coverage.

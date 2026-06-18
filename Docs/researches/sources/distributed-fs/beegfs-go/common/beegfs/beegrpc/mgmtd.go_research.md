# sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/mgmtd.go

## Purpose
`mgmtd.go` wraps the BeeGFS management gRPC client with shared connection ownership, auth-secret accessors, license verification, cleanup, and filesystem UUID retrieval.

## APIs and Control Flow
`NewMgmtd` creates a gRPC connection via `NewClientConn`, instantiates a protobuf `ManagementClient`, stores address and auth-secret bytes, and returns `Mgmtd`. `GetAuthSecret` returns the generated uint64 secret or zero, while `GetAuthSecretBytes` returns a defensive copy. `VerifyLicense` calls `GetLicense`, rejects verify errors/invalid certificates, builds zap fields for license details, checks requested feature in certificate DNS names, handles grandfathered features by valid-from date, sets `BEEGFS_LICENSED_FEATURE`, and returns details plus any error. `GetFsUUID` calls `GetNodes` and validates non-nil/non-empty UUID.

## State, Dependencies, and Integration
State includes the protobuf client, client connection, address, and auth-secret. Dependencies include BeeGFS protobuf management/license packages, auth utility, zap logging fields, slices, environment variables, and gRPC.

## Risks and Test Signals
`VerifyLicense` mutates process environment, which can leak across tests or commands. Grandfathering depends on wall-clock certificate dates. There is no listed unit test for license edge cases, auth-secret copies, cleanup idempotence, or UUID validation.

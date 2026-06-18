# sources/cloud-native/containerd/internal/dmverity/dmverity_test.go

## Purpose
Validates dm-verity metadata helpers and Linux dm-verity device workflows.

## Important APIs, Types, And Functions
`TestDMVerity` covers `IsSupported`, `Format`, `Open`, and `Close` across superblock/no-superblock and same/separate device combinations. Helper functions create loopback devices and wait for mapper nodes. `TestReadMetadata`, `TestMetadataPath`, `TestDevicePath`, and `TestErrorHandling` cover helper and failure paths.

## Control Flow
Root-only tests skip when dm-verity is unsupported, create temporary backing files, attach loop devices, format/open mappings, verify `/dev/mapper` appearance, close targets, and detach loops.

## State And Persistence
Tests create temporary files, loop devices, and device-mapper targets, then clean them up.

## Dependencies And Integration Points
Uses containerd mount loop helpers, `testutil.RequiresRoot`, docker/go-units, os/stat polling, and testify.

## Risks
Tests are environment-sensitive and require root, loop device availability, device-mapper, and dm_verity support. Failures can leave kernel resources if cleanup paths break.

## Test Signals
High integration signal for Linux verity behavior plus good unit coverage for metadata parsing.

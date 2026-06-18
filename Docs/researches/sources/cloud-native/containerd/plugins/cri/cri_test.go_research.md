<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/cri_test.go -->
# sources/cloud-native/containerd/plugins/cri/cri_test.go

## Purpose
Unit test for CRI gRPC plugin config migration.

## Important APIs, Types, And Functions
TestCRIGRPCServerConfigMigration builds old grpc.cri config map with removed and retained keys.

## Control Flow
Calls configMigration with config version 2, then asserts registry/containerd subsections were removed and streaming/TCP keys remain.

## State And Persistence
Pure in-memory map mutation.

## Dependencies And Integration Points
Exercises configMigration in cri.go.

## Risks And Edge Cases
Only tests one old version path and one plugin name; does not cover current-version no-op.

## Test Signals
Direct coverage for migration contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/cri_test.go -->

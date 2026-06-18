# sources/control-plane/csi-driver-smb/pkg/csi-common/driver_test.go

## Purpose
Unit tests for shared CSI driver metadata and capability helpers.

## Important APIs, Types, and Functions
Defines fake driver constants and `NewFakeDriver`. Tests cover `NewCSIDriver`, `GetVolumeCapabilityAccessModes`, controller/node service validation, and add helpers.

## Control Flow
Table-driven tests construct drivers with valid/missing inputs and compare expected structs or gRPC errors.

## State and Persistence
No persistence; in-memory test objects only.

## Dependencies
Uses CSI protobufs, testify/assert, reflect, and gRPC status/codes.

## Integration Points
Provides confidence for `pkg/smb.Driver` embedded capability behavior.

## Risks and Edge Cases
Some comparisons use reflect on errors, which is sensitive to exact status representation. Tests do not cover duplicate capability handling.

## Test Signals
Passing package tests validate constructor and capability semantics.

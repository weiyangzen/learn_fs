# sources/control-plane/csi-driver-smb/pkg/smb/identityserver_test.go

## Purpose
Unit tests for SMB CSI identity RPCs.

## Important APIs, Types, and Functions
Tests `GetPluginInfo`, `Probe`, and `GetPluginCapabilities` using fake drivers with missing metadata variants.

## Control Flow
Builds requests, invokes identity methods, compares errors and response fields.

## State and Persistence
In-memory only.

## Dependencies
Uses CSI protobufs, testify/assert, grpc status/codes, reflect, and testing.

## Integration Points
Validates identity behavior expected by sidecars and CSI clients.

## Risks and Edge Cases
Tests do not verify driver version content beyond empty/nonempty behavior.

## Test Signals
Expected unavailable errors for missing metadata and ready probe response.

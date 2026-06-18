# sources/control-plane/csi-driver-smb/pkg/smb/controllerserver_test.go

## Purpose
Unit tests for SMB controller behavior and helper functions.

## Important APIs, Types, and Functions
Tests controller capabilities, create/delete volume, validate capabilities, unsupported controller RPCs, expansion, volume ID parse/build, internal path helpers, `newSMBVolume`, `isValidVolumeCapabilities`, and clone helper behavior.

## Control Flow
Uses fake driver and fake mounter, sets working mount directories, builds CSI requests, and validates responses/errors across table cases. Some Windows paths are skipped or treated specially.

## State and Persistence
Creates local test directories/files under the current working directory and uses fake mounter state.

## Dependencies
Uses CSI protobufs, testify, grpc status/codes, runtime checks, os/filepath, and test utilities.

## Integration Points
Exercises controller code paths that external-provisioner depends on and internal staging calls that reuse node server logic.

## Risks and Edge Cases
Large tests include platform skips, so Windows-specific controller behavior has less assertion depth. Fake mounter does not simulate real CIFS or CSI proxy semantics.

## Test Signals
Passing tests validate parameter validation, onDelete ID semantics, clone support, and expected unimplemented RPC errors.

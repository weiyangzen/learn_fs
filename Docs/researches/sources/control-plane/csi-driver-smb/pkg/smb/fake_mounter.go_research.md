# sources/control-plane/csi-driver-smb/pkg/smb/fake_mounter.go

## Purpose
Test mounter implementation for SMB driver unit tests.

## Important APIs, Types, and Functions
Defines `fakeMounter` embedding `mount.FakeMounter`, overrides `Mount`, `MountSensitive`, and `IsLikelyNotMountPoint`, and exposes `NewFakeMounter`.

## Control Flow
Fake methods return errors when source/target/path contains sentinel substrings, otherwise success. On Windows, `NewFakeMounter` delegates to real Windows safe mounter with HostProcess flags.

## State and Persistence
No fake persistence. Windows path may create real mounter clients.

## Dependencies
Depends on runtime, strings, mount-utils, and package mounter.

## Integration Points
Used by controller/node tests to simulate mount success/failure.

## Risks and Edge Cases
Windows behavior is not actually fake, which can make tests depend on host Windows/CSI-proxy capabilities. Fake does not track mounts.

## Test Signals
`fake_mounter_test.go` validates sentinel error behavior.

# sources/control-plane/csi-driver-smb/pkg/smb/controllerserver.go

## Purpose
CSI controller implementation for dynamic SMB volume provisioning, deletion, validation, clone, and expansion metadata.

## Important APIs, Types, and Functions
Defines `smbVolume`, volume ID segment constants, `CreateVolume`, `DeleteVolume`, capability RPCs, `ControllerExpandVolume`, `internalMount`, `internalUnmount`, `copyFromVolume`, `copyVolume`, `getVolumeIDFromSmbVol`, `getInternalMountPath`, `newSMBVolume`, `getInternalVolumePath`, `smbVolToCSI`, `getSmbVolFromID`, and `isValidVolumeCapabilities`.

## Control Flow
Create validates name/capabilities/parameters, builds an SMB volume, decides whether to create a subdirectory based on secrets, explicit subDir, guest mount, or content source, internally stages the base share, creates subdirectories, optionally clones data via `cp -a`, and returns a CSI Volume. Delete parses the volume ID, locks the volume, stages the share when secrets are available and policy is not retain, deletes or archives the subdirectory, caches deletion, and unmounts.

## State and Persistence
Creates, deletes, or renames directories on the SMB share. Uses in-memory volume locks and timed deletion cache. Volume identity is encoded in a `#`-separated string containing source, subDir, uuid, and optional onDelete policy.

## Dependencies
Depends on CSI protobufs, gRPC status codes, os/filepath/fs, `cp`, klog, Azure timed cache, and node server staging methods.

## Integration Points
Called by external-provisioner. Internal mount/unmount reuses NodeStage/NodeUnstage; volume context feeds node publishing.

## Risks and Edge Cases
Volume IDs cannot safely contain `#`. Clone uses Unix `cp`, so controller clone is platform-dependent. Delete only mutates remote data when secrets are provided. Archive can overwrite after optional removal.

## Test Signals
`controllerserver_test.go` covers create/delete validation, ID encoding/parsing, onDelete policies, clone paths, capability validation, and unsupported RPCs.

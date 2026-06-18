# sources/control-plane/csi-driver-smb/test/sanity/secrets.yaml

## Purpose
This YAML supplies static SMB credentials for CSI sanity operations.

## Important APIs, Types, And Functions
It defines `NodeStageVolumeSecret` and `CreateVolumeSecret`, each with `username: sanity` and `password: sanitytestpassword`.

## Control Flow
There is no code flow. `csi-sanity` passes these secret maps into the relevant CSI RPCs.

## State, Persistence, And Dependencies
The credentials must match the local Samba container configured by `run-test.sh`.

## Integration Points
The file integrates with the SMB driver's CreateVolume and NodeStageVolume secret handling.

## Risks And Test Signals
These are test-only credentials but are still plain text. Mismatch with the Samba container causes authentication failures in CSI sanity tests. The signal is successful volume creation/staging with supplied secrets.

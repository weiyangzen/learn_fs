# sources/cloud-native/containerd/plugins/diff/lcow/lcow.go

## Purpose
Implements the Windows LCOW diff applier that converts Linux tar layers into ext4 VHD files for Linux containers on Windows.

## Important APIs, Types, And Functions
Registers the `windows-lcow` diff plugin under Windows builds. `CompareApplier` combines `diff.Applier` and `diff.Comparer`. `windowsLcowDiff.Apply` converts content to `layer.vhd`; `Compare` returns not implemented. `mountsToLayerAndParents` validates `lcow-layer` mounts. `readCounter` tracks stream size.

## Control Flow
Apply reads the content blob, walks stream processors to an OCI layer tar stream, hashes/counts bytes via `readCounter`, creates `layer.vhd`, converts tar to ext4 with whiteout handling and VHD footer, syncs the output, drains trailing data, grants VM group access, and returns an uncompressed OCI descriptor.

## State And Persistence
Writes a `layer.vhd` file into the snapshot layer directory and updates file ACLs for VM access. Content store blobs are read-only inputs.

## Dependencies And Integration Points
Uses hcsshim `tar2ext4`, Windows security helpers, content store, diff processors, plugin metadata, and Windows-specific mount type conventions. It is a fallback partner for the Windows diff service.

## Risks
Windows-only privileges and ACL setup are required. Partial VHD files are removed only on the error path before successful close. Compare is intentionally unsupported, so callers must fall back or avoid LCOW diff generation.

## Test Signals
No direct tests in this subset. Coverage is Windows integration dependent.

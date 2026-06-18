# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config/scheme.go

## Purpose
This file defines a single OSD config default constant.

## Important APIs, Types, And Functions
`WalDefaultSizeMB` is set to `576` and documented as the default WAL size in megabytes for RocksDB in BlueStore.

## Control Flow And State
There is no control flow and no state mutation. The constant is imported by OSD provisioning/configuration code that needs a default WAL size.

## Dependencies And Integration Points
The file has no imports. Its integration point is compile-time use by the OSD config package and consumers that need the BlueStore WAL default.

## Risks And Test Signals
The only risk is semantic drift if Ceph/Rook default WAL sizing changes but this constant is not updated. No direct tests in the listed set assert this constant.

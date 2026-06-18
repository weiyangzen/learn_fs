# sources/control-plane/longhorn-engine/app/cmd/volume_export.go

## Purpose
Implements `export-volume`/`export`, exporting a snapshot from a healthy replica to an external receiver.

## Important APIs, Types, and Functions
- `ExportVolumeCmd()` declares snapshot name, receiver address/port, backing image export, and HTTP timeout flags.
- `exportVolume()` validates args, finds an RW replica, verifies the snapshot disk exists, and calls `ReplicaClient.ExportVolume`.

## Control Flow
The helper validates required flags, loads controller volume info, lists replicas, picks the first `types.RW` replica, creates a replica client without instance-name validation, reads replica info, checks `rInfo.Disks` for `diskutil.GenerateSnapshotDiskName(snapshotName)`, logs export context, then invokes replica export RPC.

## State and Persistence Behavior
Read-only on the source replica snapshot data, but it streams or transfers data to the receiver. It does not alter controller/replica membership. Exported backing image inclusion is controlled by flag.

## Dependencies and Integration Points
Depends on controller client, replica client, `pkg/types`, and disk name utilities. Related to snapshot clone/file sync receiver workflows.

## Risks and Edge Cases
Choosing the first RW replica can fail if that replica lacks the snapshot while another has it; the function does not search all RW replicas. Receiver reachability and timeout handling are delegated to replica RPC. Missing snapshot disk is caught before export.

## Test Signals
No direct tests in the listed subset. Snapshot clone tests and backup tests exercise adjacent export/file-sync concepts but not this CLI path directly.

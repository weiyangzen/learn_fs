# sources/cloud-native/containerd/plugins/snapshots/devmapper/dmsetup/dmsetup.go

## Purpose
`dmsetup.go` wraps Linux `dmsetup` and related device-mapper command behavior for the devmapper snapshotter.

## Important APIs, Types, And Functions
Constants include `/dev/mapper/` and 512-byte sector size. Major APIs are `CreatePool`, `ReloadPool`, `CreateDevice`, `ActivateDevice`, `SuspendDevice`, `ResumeDevice`, `Table`, `CreateSnapshot`, `DeleteDevice`, `RemoveDevice`, `Info`, `Version`, `Status`, `GetFullDevicePath`, `BlockDeviceSize`, and `DiscardBlocks`. It defines `DeviceInfo`, `DeviceStatus`, remove options, and `ErrInUse`.

## Control Flow
Pool and thin-device functions build dmsetup table strings or messages, then execute `dmsetup`. `Info` parses column output and attribute flags. `Status` parses target status fields. Command errors are normalized by extracting Linux errno text from dmsetup output when possible. `DiscardBlocks` checks open count before invoking blkdiscard.

## State And Persistence
Commands mutate kernel device-mapper state and thin-pool metadata. This file stores no durable state itself.

## Dependencies And Integration Points
It depends on `os/exec`, `unix.Errno`, blkdiscard wrapper, and filesystem/block-device APIs. `pool_device.go` uses it for all actual device operations.

## Risks
Parsing command output is fragile across dmsetup versions/locales. `BlockDeviceSize` uses seek and assumes the path supports it. Errno extraction is best-effort string matching. Calling wrappers with wrong names can remove or mutate real devices.

## Test Signals
`dmsetup_test.go` performs root-gated integration coverage for pool creation, reload, thin devices, snapshots, status parsing, suspend/resume, discard, removal, and version.

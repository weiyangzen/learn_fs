# sources/cloud-native/containerd/internal/dmverity/dmverity_linux.go

## Purpose
Implements Linux dm-verity formatting, opening, closing, and verification using `go-dmverity` plus containerd loop-device helpers.

## Important APIs, Types, And Functions
`IsSupported` checks `/sys/module/dm_verity`. `convertToVerityParams` maps `DmverityOptions` to `verity.Params`. `Format` creates a hash tree and returns the root hash. `Open` creates read-only loop devices and opens a device-mapper verity target. `Close` closes the target. `VerifyDevice` checks device health and root hash.

## Control Flow
Formatting defaults options, computes data blocks if omitted, applies salt/UUID, and calls `verity.Create`. Opening validates root hash, chooses superblock or no-superblock params, sets up loop devices for data/hash files, calls `verity.Open`, then closes loop file handles after the kernel holds references.

## State And Persistence
Persistent effects include hash data written to the hash device and `/dev/mapper/<name>` targets. Loop devices use autoclear read-only settings.

## Dependencies And Integration Points
Depends on `core/mount`, `github.com/containerd/go-dmverity/pkg/utils`, and `verity`. Integrates with EROFS/layer integrity workflows that need transparent verified block devices.

## Risks
Requires Linux, loaded/built-in dm_verity, loop devices, device-mapper privileges, and correct offsets. Error cleanup must close loop devices on failures. Superblock versus no-superblock parameter mismatch can produce unusable mappings.

## Test Signals
Linux root tests cover support detection, same/separate device, superblock/no-superblock modes, open/close behavior, and invalid salt/UUID/root hash paths.

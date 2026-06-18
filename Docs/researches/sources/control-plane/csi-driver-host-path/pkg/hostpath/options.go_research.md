# sources/control-plane/csi-driver-host-path/pkg/hostpath/options.go

## Purpose
This file parses supported snapshot parameter options into command-line flags used when archiving filesystem volumes. Currently it supports `ignoreFailedRead` for tar-based snapshots.

## Important APIs, Types, And Functions
Constant `ignoreFailedReadParameterName` is `ignoreFailedRead`. `optionsFromParameters(vol, parameters)` returns `[]string{"--ignore-failed-read"}` when the volume is mount-access and the parameter parses as boolean true. It returns nil for absent/false values and for all block volumes. Invalid booleans on mount volumes return an error.

## Control Flow
The function first ignores all parameters for block volumes because block snapshots use file copy, not tar. For mount volumes it reads the parameter string, returns no options when empty, parses with `strconv.ParseBool`, and includes the tar option only for true.

## State, Persistence, And Dependencies
No state is persisted. Dependencies are `strconv`, `fmt`, and the `state.Volume` access type.

## Integration Points
`CreateSnapshot` and `CreateVolumeGroupSnapshot` call this before `createSnapshotFromVolume`, passing the resulting options into the `tar czf` command for filesystem snapshots.

## Risks
Only one snapshot parameter is recognized. Invalid values are deliberately ignored for block volumes, which may surprise users expecting validation to be independent of volume mode. Options are shell command arguments but not shell-expanded, so injection risk is low.

## Test Signals
Existing tests cover absent, false, true, invalid, mounted, and block volume cases. Additional integration tests should verify the tar command actually receives `--ignore-failed-read` for filesystem snapshots.

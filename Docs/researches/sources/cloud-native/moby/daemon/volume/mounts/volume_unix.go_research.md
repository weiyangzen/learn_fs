# sources/cloud-native/moby/daemon/volume/mounts/volume_unix.go

## Purpose
Unix implementation of mount resource ownership checks.

## Important APIs, Types, And Functions
`(p *linuxParser) HasResource(m *MountPoint, absolutePath string) bool` tests whether an absolute path is inside a mountpoint destination.

## Control Flow
The function computes `filepath.Rel(m.Destination, absolutePath)` and returns true when the relative path is not `..` and does not start with `../`.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Used by daemon logic that needs to determine whether a path is covered by a mountpoint, such as conflict/resource checks.

## Risks
This is lexical and destination-relative; callers must pass normalized absolute paths. Platform separator handling matters for correctness.

## Test Signals
No direct test in this subset; parser and mount tests indirectly depend on destination normalization.

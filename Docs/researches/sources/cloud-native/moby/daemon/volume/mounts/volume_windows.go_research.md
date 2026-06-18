# sources/cloud-native/moby/daemon/volume/mounts/volume_windows.go

## Purpose
Windows implementation stub for Linux parser resource ownership checks.

## Important APIs, Types, And Functions
`(p *linuxParser) HasResource(m *MountPoint, absolutePath string) bool` returns false on Windows builds.

## Control Flow
No conditional logic; all inputs produce false.

## State And Persistence
No state.

## Dependencies And Integration Points
Satisfies the `Parser` interface for build combinations where `linuxParser` still needs a Windows method implementation.

## Risks
Callers must not expect Linux-style resource coverage checks on Windows. Any Windows-specific resource logic belongs in `windowsParser.HasResource`.

## Test Signals
No direct tests; interface compilation is the primary signal.

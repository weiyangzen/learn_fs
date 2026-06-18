# sources/cloud-native/moby/daemon/volume/mounts/lcow_parser.go

## Purpose
Parser variant for Linux Containers on Windows, combining Windows host-source parsing with Linux-style container destinations.

## Important APIs, Types, And Functions
`NewLCOWParser` embeds a `windowsParser`; `lcowValidators` rejects root destinations, named pipes, and non-Linux absolute container paths. `lcowParser` overrides `ValidateMountConfig`, `ParseMountRaw`, and `ParseMountSpec`.

## Control Flow
Raw specs are split using Windows source rules plus LCOW destination regex. Parsing delegates to the Windows parser's `parseMount` but disables backslash conversion for targets and uses LCOW validators. Mount specs similarly reuse Windows source validation while preserving slash-style container targets.

## State And Persistence
No state is persisted. Parser state is limited to the embedded file-info provider.

## Dependencies And Integration Points
Used when daemon code needs LCOW semantics. Depends on shared Windows regex fragments, lazy regex compilation, Docker API mount types, and common mount validation helpers.

## Risks
Because it embeds Windows parser behavior, changes to Windows source regex or volume-name validation affect LCOW. Named pipe rejection and root normalization are security/compatibility-sensitive.

## Test Signals
`lcow_parser_test.go` covers valid/invalid raw specs, reserved names, file-vs-directory source checks, root target rejection, no named-pipe support, and parsed `MountPoint` fields.

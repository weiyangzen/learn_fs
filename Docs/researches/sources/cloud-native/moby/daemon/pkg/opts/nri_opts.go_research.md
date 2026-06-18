<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/nri_opts.go -->
# sources/cloud-native/moby/daemon/pkg/opts/nri_opts.go

## Purpose
Parses daemon NRI configuration from JSON and command-line flag values.

## Important APIs, Types, And Functions
`NRIOpts` contains `Enable`, `PluginPath`, `PluginConfigPath`, and `SocketPath`. `UnmarshalJSON` rejects unknown fields. `NamedNRIOpts` implements `Set`, `Type`, `String`, and `Name`.

## Control Flow
JSON decoding uses `DisallowUnknownFields`. CLI parsing reads one CSV record, splits each field at `=`, treats bare `enable` as `enable=true`, parses booleans with `strconv.ParseBool`, stores path strings, and rejects unknown keys.

## State, Dependencies, And Integration Points
State is the referenced `NRIOpts` struct. It integrates with daemon config/flags for Node Resource Interface support.

## Risks And Test Signals
Path values are accepted without filesystem validation. CSV parsing supports quoted commas but a missing `=` for path keys silently sets an empty path. Tests cover JSON strictness, CLI booleans, path serialization, and unknown keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/nri_opts.go -->

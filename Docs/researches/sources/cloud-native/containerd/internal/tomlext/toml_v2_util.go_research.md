# sources/cloud-native/containerd/internal/tomlext/toml_v2_util.go

## Purpose
Defines a TOML/JSON-friendly duration wrapper around `time.Duration`.

## Important APIs, Types, And Functions
`Duration` is a named `time.Duration`. `UnmarshalText` parses Go duration strings. `MarshalText` serializes using `time.Duration.String`. `ToStdTime` and `FromStdTime` convert to/from standard duration.

## Control Flow
Text unmarshalling receives bytes from TOML decoding, parses them, and stores the converted duration.

## State And Persistence
Values are persisted in configuration as strings such as `5s` or `1m0s`.

## Dependencies And Integration Points
Uses `time`. NRI config uses this type for plugin registration/request timeouts.

## Risks
Only Go duration syntax is accepted; plain integer TOML durations are not. String formatting may normalize input representation.

## Test Signals
No direct tests in this subset. Indirect coverage through config parsing tests elsewhere.

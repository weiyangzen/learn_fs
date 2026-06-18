<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/nri_opts_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/nri_opts_test.go

## Purpose
Verifies JSON and command-line parsing for daemon NRI options.

## Important APIs, Types, And Functions
`TestNRIOptsJSON` directly invokes `NRIOpts.UnmarshalJSON`. `TestNRIOptsCmd` uses `NewNamedNRIOptsRef`, `Set`, and `String`.

## Control Flow
JSON tests compare decoded structs and assert unknown-field errors. Command tests set CLI strings and compare expected struct fields plus serialized output; bare `enable` is expected to mean true.

## State, Dependencies, And Integration Points
No external state. The tests protect daemon config parsing for NRI enablement and path settings.

## Risks And Test Signals
They do not cover invalid boolean strings, quoted CSV, duplicate keys, or empty path semantics. They strongly signal that unknown JSON and CLI keys must be rejected.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/nri_opts_test.go -->

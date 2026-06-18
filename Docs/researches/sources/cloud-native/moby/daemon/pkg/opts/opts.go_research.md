<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/opts.go -->
# sources/cloud-native/moby/daemon/pkg/opts/opts.go

## Purpose
Centralizes generic flag value containers and validators used by Docker daemon configuration.

## Important APIs, Types, And Functions
`ListOpts`, `MapOpts`, `MapMapOpts`, and named wrappers implement pflag-style behavior. Validators include `ValidateIPAddress`, `ValidateDNSSearch`, `ValidateLabel`, `ValidateSingleGenericResource`, `ParseLink`, and `MemBytes` JSON/flag parsing.

## Control Flow
List and map setters optionally call validators before appending or storing values. DNS validation trims spaces and uses lazy regexps. Label validation requires `=` and blocks reserved Docker namespaces. `ParseLink` handles `name:alias`, short format, and legacy `/container:/path/alias`. `MemBytes` delegates to `go-units`.

## State, Dependencies, And Integration Points
State is held in referenced slices/maps. It depends on `netip`, regex helpers, `go-units`, and standard string/path utilities. Many daemon flags compose these primitives.

## Risks And Test Signals
Map iteration makes String output order unstable. Validators are intentionally permissive in some places. `opts_test.go` covers major value-container behavior and validator edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/opts.go -->

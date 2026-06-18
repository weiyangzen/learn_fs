# sources/cloud-native/soci-snapshotter/version/version.go

## Purpose
`version.go` defines package-level version metadata filled at link time.

## Important APIs, Types, and Functions
`const Unset = "<unknown>"`. Variables `Version` and `Revision` default to `Unset` and are intended to be overwritten via linker flags from the Makefile.

## Control Flow, State, and Persistence
There is no control flow or persistence. State is process-global package variables initialized at startup.

## Dependencies and Integration Points
The file has no imports. The Makefile injects values with `-X <pkg>/version.Version=...` and `-X <pkg>/version.Revision=...`.

## Risks and Test Signals
Tests or binaries built without the expected linker flags may retain `<unknown>`. The paired test only checks `Version`, not `Revision`.

# sources/cloud-native/containers-storage/drivers/jsoniter.go

## Purpose
`jsoniter.go` defines the package-level JSON codec used by graphdriver helpers.

## Important APIs, Types, And Functions
`var json = jsoniter.ConfigCompatibleWithStandardLibrary` exposes a standard-library-compatible JSON API.

## Control Flow
`chown.go` uses this variable to marshal and unmarshal ID-map configuration for the reexec chown helper.

## State And Persistence
No persistent state. The variable is an in-memory codec configuration.

## Dependencies And Integration Points
It depends on `github.com/json-iterator/go` and avoids repeated imports or naming conflicts across graphdriver files.

## Risks
Compatibility with standard library JSON is expected; changing config could affect reexec protocol encoding.

## Test Signals
Indirectly tested by chown reexec flows.

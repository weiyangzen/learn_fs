# sources/cloud-native/containers-storage/drivers/overlay/jsoniter.go

## Purpose
`overlay/jsoniter.go` defines the overlay package's standard-compatible JSON codec.

## Important APIs, Types, And Functions
`var json = jsoniter.ConfigCompatibleWithStandardLibrary` is used by overlay reexec and metadata flows.

## Control Flow
`mount.go` uses this codec to encode/decode `mountOptions` across a reexec stdin pipe.

## State And Persistence
No persistent state. The codec configuration is package-level runtime state.

## Dependencies And Integration Points
It depends on `github.com/json-iterator/go` and avoids repeating codec setup across overlay files.

## Risks
The reexec protocol expects standard JSON compatibility. Changing codec behavior could break option transport.

## Test Signals
Indirectly tested by overlay mount reexec paths.

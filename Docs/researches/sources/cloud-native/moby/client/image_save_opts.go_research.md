# sources/cloud-native/moby/client/image_save_opts.go

## Purpose
`image_save_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `ImageSaveOption`, `imageSaveOptionFunc`, `imageSaveOpts`, `imageSaveOptions`. Option helpers: `Apply`, `ImageSaveWithPlatforms`. Fields: `imageSaveOpts` includes `apiOptions`; `imageSaveOptions` includes `Platforms`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.

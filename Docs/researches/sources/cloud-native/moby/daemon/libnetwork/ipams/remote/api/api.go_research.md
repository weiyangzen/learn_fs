# sources/cloud-native/moby/daemon/libnetwork/ipams/remote/api/api.go

## Purpose
Defines JSON-serializable request and response structures for the remote IPAM plugin protocol.

## Important APIs, Types, And Functions
- `Response` embeds the common plugin `Error` string and implements `IsSuccess` and `GetError`.
- `GetCapabilityResponse` and `ToCapability` convert plugin capability fields to `ipamapi.Capability`.
- `GetAddressSpacesResponse`, `RequestPoolRequest`, `RequestPoolResponse`, `ReleasePoolRequest`, `ReleasePoolResponse`, `RequestAddressRequest`, `RequestAddressResponse`, `ReleaseAddressRequest`, and `ReleaseAddressResponse` model plugin RPC payloads.

## Control Flow
This file contains no RPC logic. The remote allocator sends these structures through the plugin client and checks the embedded `Response`.

## State And Persistence
No state. Payloads are transient request/response values.

## Dependencies And Integration Points
Depends on `ipamapi` only for capability conversion. Used by `remote.go` and remote plugin tests.

## Risks
Protocol fields are exported and stringly typed for JSON compatibility. Remote plugins must return CIDR-formatted pools and addresses; parsing errors surface later in `remote.go`.

## Test Signals
`remote_test.go` uses these payload shapes through an HTTP test plugin, including capabilities, default address spaces, pool data, and address responses.

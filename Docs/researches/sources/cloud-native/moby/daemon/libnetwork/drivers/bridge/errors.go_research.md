<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/errors.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/errors.go

## Purpose
Centralizes bridge-driver error types so callers can classify invalid gateway, network ID, and endpoint ID failures through Docker/containerd error interfaces.

## Important APIs, Types, And Functions
`errInvalidGateway` is an `errdefs.InvalidParameter` error used when a configured gateway is outside the network. `invalidNetworkIDError` implements `Error` and `NotFound`. `invalidEndpointIDError` implements `Error` and `InvalidParameter`. `endpointNotFoundError` implements `Error` and `NotFound`.

## Control Flow
There is no complex control flow; bridge driver operations construct these values at validation and lookup failure points. Error interface marker methods determine higher-level API classification.

## State And Persistence
No state is stored. The file affects persisted API behavior indirectly because clients and tests depend on stable error categories and messages.

## Dependencies And Integration Points
Depends on `errdefs` and standard `errors`/`fmt`. Integrated by network and endpoint create/delete/join paths and setup validation logic.

## Risks And Edge Cases
Changing message strings or marker methods can break API expectations and tests such as invalid endpoint deletion/creation checks. The gateway error is a package variable, so callers should wrap it carefully if more context is needed.

## Test Signals
Bridge tests assert `InvalidArgument` or `NotFound` style behavior for empty endpoint IDs, duplicate operations, invalid gateways, and missing endpoints/networks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/errors.go -->

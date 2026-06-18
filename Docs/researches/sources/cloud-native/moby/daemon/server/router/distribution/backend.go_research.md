# sources/cloud-native/moby/daemon/server/router/distribution/backend.go

## Purpose
`backend.go` defines the narrow backend contract required by the distribution inspection router.

## Important APIs, Types, And Functions
`Backend` exposes `GetRepositories(context.Context, reference.Named, *registry.AuthConfig) ([]distribution.Repository, error)`.

## Control Flow
The route code parses and validates image references, decodes auth headers, and then uses this interface to obtain one or more registry repositories/endpoints to inspect.

## State And Persistence
The interface itself has no state. Implementations may open registry connections and consult daemon registry configuration but do not persist state through this contract.

## Dependencies And Integration Points
It depends on Docker distribution repository interfaces, distribution references, and API registry auth config.

## Risks
The interface hides endpoint ordering and mirror behavior; route behavior depends on implementations returning repositories in the correct fallback order.

## Test Signals
Compilation of the distribution router against daemon registry backends is the primary signal.

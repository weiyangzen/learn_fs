# sources/cloud-native/moby/daemon/cluster/errors.go

## Purpose
Defines typed swarm errors that map to Docker API error categories such as forbidden, unavailable, invalid parameter, unauthorized, and conflict.

## Important APIs, Types, And Functions
Defines swarm error constants `errNoSwarm`, `errSwarmExists`, `errSwarmJoinTimeoutReached`, `errSwarmLocked`, `errSwarmCertificatesExpired`, and `errSwarmNotManager`. Defines types `notAllowedError`, `notAvailableError`, `configError`, `invalidUnlockKey`, and `notLockedError` with marker methods.

## Control Flow
No complex control flow. Each error type implements `Error` and a marker method consumed by Docker error classification.

## State And Persistence
No state.

## Dependencies And Integration Points
Used across cluster lifecycle and manager-only APIs, then classified by API error handling through marker interfaces.

## Risks And Test Signals
Changing strings changes user-facing API/CLI messages; changing marker methods changes HTTP status mapping. Compile-time and API tests elsewhere provide coverage.

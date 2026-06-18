# sources/cloud-native/moby/daemon/server/router/swarm/helpers_test.go

## Purpose
This test verifies that `adjustForAPIVersion` removes or preserves swarm service-spec fields at expected API version boundaries.

## Important APIs, Types, And Functions
`TestAdjustForAPIVersion` builds a service spec with sysctls, credential specs, config references, ulimits, tmpfs options, placement max replicas, pids limit, and resource swap/memory-swappiness pointers.

## Control Flow
The test applies `adjustForAPIVersion` with descending API versions and checks that fields remain for newer versions and are stripped for older versions.

## State And Persistence
No daemon state is persisted; the test validates in-memory request mutation.

## Dependencies And Integration Points
Depends on API swarm/container/mount types and the helper under test.

## Risks
The test intentionally does not verify every possible service field, so new version gates need new assertions.

## Test Signals
Provides focused regression coverage for version-gated swarm service fields.

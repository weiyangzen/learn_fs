# sources/cloud-native/moby/daemon/volume/drivers/extpoint_test.go

## Purpose
Basic unit coverage for driver store lookup and registration.

## Important APIs, Types, And Functions
`TestGetDriver` exercises `NewStore`, `GetDriver`, and `Register` with a fake volume driver.

## Control Flow
The test verifies that a missing driver returns an error, registers a fake driver under the name `fake`, retrieves it, and checks that the returned driver reports the expected name.

## State And Persistence
Only in-memory store state is mutated.

## Dependencies And Integration Points
Uses `daemon/volume/testutils.NewFakeDriver` to satisfy `volume.Driver` without a real plugin.

## Risks
The test does not exercise plugin discovery, acquire/release modes, duplicate registration, invalid scopes, or `GetAllDrivers`.

## Test Signals
Confirms the core extension map behavior and missing-driver path remain stable.

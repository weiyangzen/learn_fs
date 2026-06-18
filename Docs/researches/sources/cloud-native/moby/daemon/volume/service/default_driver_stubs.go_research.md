# sources/cloud-native/moby/daemon/volume/service/default_driver_stubs.go

## Purpose
Platform stub for default driver setup where the local driver is not registered by this build.

## Important APIs, Types, And Functions
`setupDefaultDriver(_ *drivers.Store, _ string, _ idtools.Identity) error { return nil }`.

## Control Flow
No-op success.

## State And Persistence
No state is created or loaded.

## Dependencies And Integration Points
Maintains `NewVolumeService` compilation on platforms/build tags without the local driver setup implementation.

## Risks
Services on stub platforms will not have a default local driver unless registered elsewhere.

## Test Signals
Build success on covered platforms is the primary signal.

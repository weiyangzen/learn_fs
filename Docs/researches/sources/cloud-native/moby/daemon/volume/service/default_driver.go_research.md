# sources/cloud-native/moby/daemon/volume/service/default_driver.go

## Purpose
Registers the built-in local volume driver during volume service startup on supported platforms.

## Important APIs, Types, And Functions
`setupDefaultDriver(store *drivers.Store, root string, rootIDs idtools.Identity) error` creates a local driver and registers it under `volume.DefaultDriverName`.

## Control Flow
The function calls `local.New(root, rootIDs)`, returns creation errors, and registers the resulting driver in the driver store.

## State And Persistence
Initializes the local driver's on-disk volume root and loads any existing local volumes through `local.New`.

## Dependencies And Integration Points
Called by `NewVolumeService`. Depends on the local driver, driver store, default driver name, and root identity.

## Risks
If registration fails due to an existing driver name, this implementation does not surface that boolean; local initialization errors are the main startup failure path.

## Test Signals
Service tests often construct stores manually; local driver behavior is covered by local package tests and Linux service size tests.

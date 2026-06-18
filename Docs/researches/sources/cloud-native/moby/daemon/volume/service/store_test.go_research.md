# sources/cloud-native/moby/daemon/volume/service/store_test.go

## Purpose
Unit tests for `VolumeStore` creation, removal, listing, filtering, references, plugin reference cleanup, and get behavior.

## Important APIs, Types, And Functions
Tests include `TestCreate`, `TestRemove`, `TestList`, `TestFindByDriver`, `TestFindByReferenced`, `TestDerefMultipleOfSameRef`, `TestCreateKeepOptsLabelsWhenExistsRemotely`, `TestDefererencePluginOnCreateError`, `TestRefDerefRemove`, `TestGet`, `TestGetWithReference`, and `TestFilterFunc`.

## Control Flow
Tests register fake drivers, create volumes with labels/options/references, assert unknown driver and driver create errors, remove referenced/unreferenced volumes, verify persistence across store restart, filter by driver/dangling, release duplicate refs, preserve labels for remotely existing volumes, ensure plugin acquire refs are released after create error, and validate slice filtering cases.

## State And Persistence
Uses temporary Bolt metadata stores, fake in-memory drivers, and a fake HTTP plugin server for reference-count behavior.

## Dependencies And Integration Points
Exercises store, driver store, plugin adapter path, options, fake drivers/plugins, error wrappers, and cmp rules for wrapped volumes.

## Risks
Fake drivers are simpler than real plugins and do not cover slow/unavailable plugin list behavior. Some tests rely on string comparisons for driver-originated errors.

## Test Signals
Broad regression signal for store correctness, especially reference protection and plugin refcount cleanup.

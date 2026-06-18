# sources/cloud-native/moby/daemon/volume/service/restore_test.go

## Purpose
Unit test for volume metadata restoration after store restart.

## Important APIs, Types, And Functions
`TestRestore` creates a store, writes volumes with and without labels/options, shuts it down, creates a new store over the same root, and reads volumes back.

## Control Flow
The test registers a fake driver, creates `test1` with nil metadata and `test2` with labels/options, closes the store, reopens it, retrieves both volumes, and asserts `DetailedVolume` options/labels are nil for the first and equal to original maps for the second.

## State And Persistence
Persists data in temporary `metadata.db` and fake driver memory across store restarts.

## Dependencies And Integration Points
Validates `NewStore`, `restore`, metadata helpers, fake driver, and detailed volume wrapping.

## Risks
Does not cover stale metadata removal, missing drivers, plugin refcounts, or metadata entries without driver names.

## Test Signals
Strong signal that labels/options are not lost across daemon store restart.

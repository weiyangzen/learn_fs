# sources/cloud-native/moby/daemon/volume/service/db_test.go

## Purpose
Unit tests for BoltDB volume metadata helpers.

## Important APIs, Types, And Functions
`TestSetGetMeta` opens a temporary Bolt database, constructs a `VolumeStore`, and exercises `getMeta`/`setMeta`.

## Control Flow
The test verifies `getMeta` errors when the bucket is absent, creates the bucket, verifies a missing key returns zero `volumeMetadata`, writes metadata with driver, labels, and options, and reads it back exactly.

## State And Persistence
Creates a temporary bbolt database file and closes it through `store.Shutdown`.

## Dependencies And Integration Points
Validates metadata persistence used by store create/restore paths.

## Risks
Does not test `removeMeta`, `listMeta`, corrupt JSON, or concurrent transactions.

## Test Signals
Good signal for JSON round-trip and missing metadata semantics.

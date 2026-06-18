# sources/cloud-native/moby/daemon/volume/service/db.go

## Purpose
BoltDB metadata persistence for volume name, driver, labels, and options.

## Important APIs, Types, And Functions
Defines `volumeBucketName`, `volumeMetadata`, and helpers `setMeta`, `getMeta`, `removeMeta`, and `listMeta` with store receiver wrappers.

## Control Flow
`setMeta` JSON-marshals metadata, creates the bucket if needed, and writes by volume name. `getMeta` reads the bucket and unmarshals when a value exists, returning zero metadata for missing keys. `removeMeta` deletes by key. `listMeta` iterates all bucket values during restore, skips empty values, logs malformed JSON, and returns valid metadata entries.

## State And Persistence
Persists metadata in `<root>/volumes/metadata.db` under the `volumes` bucket.

## Dependencies And Integration Points
Used by `VolumeStore.create`, `getVolume`, `purge`, `Remove`, and `restore`. Depends on bbolt and JSON.

## Risks
Store receiver methods assume `s.db` is non-nil; an in-memory store with empty root would panic if metadata methods are used. `removeMeta` assumes bucket exists. Corrupt metadata is logged and skipped during restore.

## Test Signals
`db_test.go` covers missing bucket behavior, zero metadata for missing key, and round-trip labels/options.

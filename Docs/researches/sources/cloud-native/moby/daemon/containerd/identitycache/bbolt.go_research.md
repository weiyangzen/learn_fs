# sources/cloud-native/moby/daemon/containerd/identitycache/bbolt.go

## Purpose
Implements a bbolt-backed persistent image identity cache with corruption recovery and explicit pruning of expired or invalid records.

## Important APIs, Types, And Functions
- `NewBoltDBBackend(root)` creates `<root>/image/identity-cache.db`, initializes bucket `image-identity-cache-v1`, or returns a no-op backend for empty root.
- `Load`, `Store`, `Walk`, `PruneExpired`, and `Close` implement `Backend`.
- `safeOpen`, `fallbackOpen`, and `fileHasContent` recover from corrupt non-empty database files by renaming them to timestamped `.bak` files.

## Control Flow
Loads copy raw bbolt values out of a read transaction, unmarshal JSON, delete corrupt entries, and treat expired entries as misses without deleting them. Stores marshal entries and put them in the bucket. Walk iterates all decodable entries and honors context cancellation. Pruning deletes entries that are expired or no longer JSON-decodable.

## State And Persistence
Persists cache entries as JSON values keyed by cache key in a bbolt bucket under daemon root. `Close` is idempotent through `sync.Once`. Corruption recovery preserves the old file as a backup and starts with a new empty DB.

## Dependencies And Integration Points
Depends on bbolt, filesystem permissions, containerd logging, and the identitycache backend interface. It is used by the image service identity cache to survive daemon restarts.

## Risks And Edge Cases
Expired loads do not delete entries, so prune maintenance must run to bound disk usage. Corrupt JSON entries are silently dropped on load and deleted on prune. `safeOpen` recovers only when the DB file has content; empty-file open failures are returned.

## Test Signals
`bbolt_test.go` checks expired entries remain visible to walk until prune and that expired loads miss without deleting. Image identity tests verify persistence across restart and refresh of expired persisted entries.

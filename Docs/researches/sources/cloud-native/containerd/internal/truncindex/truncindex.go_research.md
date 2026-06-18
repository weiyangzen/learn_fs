# sources/cloud-native/containerd/internal/truncindex/truncindex.go

## Purpose
Provides Docker-compatible lookup of full IDs by unique prefixes using a Patricia trie.

## Important APIs, Types, And Functions
Errors include `ErrEmptyPrefix`, `ErrIllegalChar`, `ErrNotExist`, and `ErrAmbiguousPrefix`. `TruncIndex` owns a trie and full-ID set. `NewTruncIndex`, `Add`, `Delete`, `Get`, and `Iterate` are public.

## Control Flow
Add validates non-empty/no-space/unique IDs and inserts into both map and trie. Delete requires an exact full ID. Get visits the prefix subtree and returns the only matching full ID or ambiguity/not-exist errors. Iterate locks and visits all trie entries.

## State And Persistence
In-memory trie and map protected by an RW mutex. No persistence.

## Dependencies And Integration Points
Uses `github.com/tchap/go-patricia/v2/patricia`. Used wherever containerd wants shorthand ID resolution.

## Risks
`Iterate` holds the write lock and warns handlers not to call public methods, which would deadlock. Add is not rollback-safe if trie insert failed after map insert, though failures are unlikely.

## Test Signals
No direct tests listed in this subset. Behavior likely covered by Docker-derived or container ID lookup tests elsewhere.

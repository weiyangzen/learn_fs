# sources/cloud-native/moby/daemon/containerd/identitycache/bbolt_test.go

## Purpose
Tests bbolt identity cache expiry semantics, specifically the distinction between load-time misses and explicit prune-time deletion.

## Important APIs, Types, And Functions
- `TestBoltBackendWalkIncludesExpiredEntriesUntilPrune` stores fresh and expired entries, walks before/after prune, and compares keys.
- `TestBoltBackendLoadExpiredReturnsMissWithoutDelete` verifies `Load` misses expired entries while `Walk` can still see them before pruning.

## Control Flow
Each test creates a temp bbolt backend, stores entries with controlled timestamps, then calls backend APIs with a fixed `now`. The first test sorts walked keys for deterministic comparison.

## State And Persistence
Uses temporary on-disk bbolt databases and closes them with `defer`. The tests validate durable backend behavior, not in-memory image service cache behavior.

## Dependencies And Integration Points
Uses `gotest.tools` assertions and the bbolt backend constructor. It guards assumptions made by image identity maintenance, where refresh can inspect expired persisted entries before pruning.

## Risks And Edge Cases
These tests do not exercise corruption recovery or JSON decode failures. They intentionally assert that expired records can remain on disk, so any future eager-delete design would require coordinated test and maintenance changes.

## Test Signals
Failures indicate changed backend expiry semantics that could break cache refresh, pruning, or disk-bounding behavior.

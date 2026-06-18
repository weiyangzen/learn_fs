# sources/cloud-native/containerd/core/metadata/db.go

## Purpose

This file defines the metadata database object that coordinates bbolt metadata, content and snapshot backends, migrations, mutation callbacks, event publishing, collectible resource registration, and garbage collection.

## Important APIs, Types, and Functions

Constants `schemaVersion` and `dbVersion` define the DB schema. Options include `WithPolicyIsolated` and `WithEventsPublisher`. `DB` holds the transactor, snapshotters, content store, GC locks/dirty flags, callbacks, collectors, and options. Public methods include `NewDB`, `Close`, `Init`, `ContentStore`, `Snapshotter`, `Snapshotters`, `View`, `Update`, `Publisher`, `RegisterMutationCallback`, `RegisterCollectibleResource`, and `GarbageCollect`. `GCStats` reports phase durations. Internal helpers include `publishEvents`, `getMarked`, `cleanupSnapshotter`, and `cleanupContent`.

## Control Flow

`NewDB` wraps the backend content store and snapshotters. `Init` opens a write transaction, discovers current schema/version by scanning migrations backward, applies needed migrations, creates the v1 bucket, and stores the current DB version, using a sentinel error to skip no-op commits. `Update` takes the GC read lock, runs a write transaction, and invokes mutation callbacks with dirty status on success. `GarbageCollect` takes the GC write lock, builds a collection context, marks reachable nodes, opens a write transaction to remove unmarked metadata nodes and set dirty backend flags, resets dirty counters, schedules event publication plus backend snapshot/content cleanup, finishes custom collectors, releases the lock, then waits for async cleanup.

## State and Persistence Behavior

The DB persists all metadata under bbolt schema `v1`. Dirty flags track deletions requiring GC, including which snapshotters and whether content need backend cleanup. Garbage collection removes metadata records first, then separately asks snapshotter/content backends to remove unreferenced data. Events are published only after successful metadata commit.

## Dependencies and Integration Points

It integrates bbolt, content stores, snapshotters, metadata migrations, events, namespace context, GC graph package, log/tracing through callers, and custom collectible resource collectors. Other metadata store implementations use `DB.Update` and `DB.View`.

## Risks and Edge Cases

Operations using a context transaction can bypass `DB.Update` callback timing. GC holds a write lock through marking and metadata sweep but releases before waiting for backend cleanup; this limits mutation during mark/sweep while allowing cleanup to continue. Collector start failures silently skip that resource type for the round. Event publication is asynchronous and logs failures rather than failing GC. Schema migration correctness is critical because all stores share bucket constants.

## Test Signals

`db_test.go` covers initialization versioning, migration cases, metadata collector behavior, GC benchmarking, helper store construction, and close semantics. Additional tests should cover mutation callbacks, event publishing after GC removals, isolated policy construction, collector start failure, and concurrent update/GC interactions.

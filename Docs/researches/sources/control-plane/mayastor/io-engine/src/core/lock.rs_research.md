# sources/control-plane/mayastor/io-engine/src/core/lock.rs

## Purpose
Provides an async resource lock manager for serializing global, subsystem, and per-resource operations such as nexus, pool, and replica mutations.

## Important APIs, Types, and Functions
- `ProtectedSubsystems` defines common IDs: `NEXUS`, `POOL`, and `REPLICA`.
- `ResourceLockManagerConfig::with_subsystem` declares subsystem lock shards.
- `ResourceLockManager::initialize`, `get_instance`, `lock`, and `get_subsystem` manage global access.
- `ResourceSubsystem::lock` and `lock_resource` acquire subsystem-level or hashed object-level locks.
- `ResourceLockGuard` releases on drop.

## Control Flow and State
Startup initializes a singleton `ResourceLockManager` from config. Each subsystem owns a vector of async mutexes for hashed object locks plus one subsystem-wide mutex. `acquire_lock` supports optional timeout, immediate try-lock, or indefinite wait, then increments `num_acquires` and returns a guard.

State is process-local lock state and simple acquisition counters. There is no persistence.

## Dependencies and Integration Points
Uses `futures::lock::Mutex`, `tokio::time::timeout`, and `OnceCell`. The main binary initializes it; gRPC v0/v1 pool, replica, nexus, stats, and snapshot handlers use it to serialize control-plane operations.

## Risks and Test Signals
Resource locks are hash-sharded, so different resource IDs can collide and serialize unexpectedly. `get_instance` and unknown subsystem lookup panic. `try_lock` is ignored when a timeout is supplied. Tests should cover initialization, duplicate subsystem panic, timeout behavior, try-lock behavior, hash-lock mutual exclusion, and integration with gRPC operations that must not deadlock.

# sources/distributed-fs/eos/mgm/tgc/TestingTapeGc.hh

## Purpose
Provides a thin test-only subclass of `TapeGc` that exposes the core protected eviction method.

## Important APIs, types, and functions
`TestingTapeGc` forwards constructor arguments to `TapeGc` and uses `using TapeGc::tryToGarbageCollectASingleFile;` to make that method public for unit tests.

## Control flow
Tests can instantiate `TestingTapeGc` with a fake `ITapeGcMgm`, push accesses through `fileAccessed()`, and invoke one eviction attempt without starting a worker thread.

## State and persistence behavior
No new state is added. All state and side effects are inherited from `TapeGc`.

## Dependencies and integration points
Depends directly on `TapeGc.hh`. It is intended for TGC unit tests that need deterministic, single-step garbage collection.

## Risks and test signals
The class intentionally breaks encapsulation for testing, so tests should avoid relying on unrelated protected internals. It is useful for verifying each branch in `tryToGarbageCollectASingleFile()` without sleeps or background-thread timing.

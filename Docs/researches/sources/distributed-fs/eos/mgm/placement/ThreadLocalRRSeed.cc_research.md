<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.cc -->
# sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.cc

Source read size: 46 lines, 1038 bytes.

## Purpose

Implements the thread-local round-robin seed vector used by thread-local placement strategy mode.

## Important APIs, Types, and Functions

Defines `thread_local std::vector<uint64_t> ThreadLocalRRSeed::gRRSeeds`, plus `init`, `resize`, and `get`.

## Control Flow

`init` resizes the thread-local vector and optionally fills every seed with a random initial value. `resize` preserves existing seeds and optionally randomizes newly added entries. `get` returns the current seed for an index and advances it by `n_items`, logging a critical error and returning zero when the index is out of range.

## State and Persistence Behavior

State is per-thread memory only. It is not shared across threads and is reset when a thread exits or reinitializes the vector.

## Dependencies and Integration Points

Used by `ThreadLocalRRSeeder` in the round-robin placement strategy. Depends on EOS logging and random utilities.

## Risks and Edge Cases

Thread-local state means scheduling fairness is per worker thread, not global. Calling `init` can reset existing seeds in the current thread. Out-of-range access returns zero, which biases selection instead of failing the placement.

## Test Signals

Test independent seed sequences across threads, randomized initialization bounds, resize preserving old values, out-of-range handling, and repeated `get` increments by replica count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.cc -->

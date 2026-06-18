<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.hh -->
# sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.hh

Source read size: 32 lines, 760 bytes.

## Purpose

Declares the thread-local round-robin seed holder for placement scheduling.

## Important APIs, Types, and Functions

Defines `kDefaultMaxRRSeeds` and struct `ThreadLocalRRSeed` with static `get`, `init`, `resize`, `getNumSeeds`, and thread-local `gRRSeeds`.

## Control Flow

The header exposes only static functions; concrete behavior is implemented in the `.cc` file and consumed through `ThreadLocalRRSeeder`.

## State and Persistence Behavior

The only state is a thread-local vector of `uint64_t` seeds. It is process memory with per-thread lifetime.

## Dependencies and Integration Points

Included by `RoundRobinPlacementStrategy.hh` and used by the thread-local round-robin strategy.

## Risks and Edge Cases

Users must call `init` or rely on the default 1024-entry vector before requesting indexes. Different threads may produce different placement sequences for identical workloads.

## Test Signals

Compile coverage, default seed count, explicit init/resize behavior, and integration with `RoundRobinPlacement` using `kThreadLocalRoundRobin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.hh -->

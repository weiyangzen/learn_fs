<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/random.cc -->
# sources/distributed-fs/lizardfs/src/common/random.cc

## Purpose
Defines and seeds the project-global random engine. The source was read completely for this report.

## Important APIs, Types, And Functions
`RandomEngine kRandomEngine` and `rnd_init()` are implemented. `rnd_init` seeds the global `std::mt19937` from `std::random_device` and returns 0.

## Control Flow
Control flow is a single seed assignment.

## State And Persistence Behavior
Global mutable RNG state persists for the process lifetime; no disk persistence.

## Dependencies And Integration Points
Used by `random.h` helpers and tests/algorithms needing random values.

## Risks And Edge Cases
The global engine is not synchronized and deterministic tests must seed/initialize carefully. `random_device` quality varies by platform.

## Test Signals
Tests should seed deterministically when reproducibility matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/random.cc -->

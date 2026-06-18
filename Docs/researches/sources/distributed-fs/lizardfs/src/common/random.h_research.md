<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/random.h -->
# sources/distributed-fs/lizardfs/src/common/random.h

## Purpose
Declares the project random engine and templated uniform integer helpers. The source was read completely for this report.

## Important APIs, Types, And Functions
`RandomEngine`, `kRandomEngine`, `rnd_init`, `rnd<T>`, and `rnd_ranged<T>` are public.

## Control Flow
`rnd` returns a value over the full distribution range; `rnd_ranged` asserts positive range and returns [0, range).

## State And Persistence Behavior
State is the extern global `std::mt19937`.

## Dependencies And Integration Points
Used by tests and utility algorithms.

## Risks And Edge Cases
Unsigned/signed template use follows `std::uniform_int_distribution` constraints; global engine is not thread-safe.

## Test Signals
Unit tests should cover range bounds and deterministic seeded behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/random.h -->

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/SampleDataForTests.java

## Purpose
`SampleDataForTests` centralizes common null, empty, and non-empty sample arrays/lists for prefetch tests.

## Important APIs, Types, And Functions
It is a final utility class with a private constructor and public constants for object, byte, short, int, long arrays, plus lists: `NULL_*`, `EMPTY_*`, `NON_EMPTY_*`, `EMPTY_LIST`, and `VALID_LIST`.

## Control Flow
There is no runtime flow; constants are initialized at class load.

## State And Persistence
State is static final in-memory sample data. The empty/valid lists are mutable list instances from `ArrayList`/`Arrays.asList`, so tests should not mutate them unexpectedly.

## Dependencies And Integration Points
It imports Java collections only and is intended for use by prefetch validation tests.

## Risks
Shared mutable constants can cause cross-test pollution if modified. Primitive array constants with length 1 do not encode meaningful contents, only presence.

## Test Signals
Signals are clearer argument-check tests using standardized null/empty/non-empty inputs.

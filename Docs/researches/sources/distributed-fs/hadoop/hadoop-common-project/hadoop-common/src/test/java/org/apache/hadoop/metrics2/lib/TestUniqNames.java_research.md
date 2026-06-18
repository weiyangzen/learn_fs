# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestUniqNames.java

## Purpose
Small unit test for `UniqueNames`, confirming that duplicate metric/source names are made unique with numeric suffixes.

## Important APIs, Types, And Functions
Uses `UniqueNames.uniqueName(String)` and JUnit `assertEquals`.

## Control Flow
`testCommonCases()` requests `foo` twice and expects `foo`, then `foo-1`. `testCollisions()` pre-allocates `foo`, then requests existing suffixed names and base names to prove collision handling recurses to available variants.

## State And Persistence Behavior
State is an in-memory `UniqueNames` instance per test. No external persistence exists.

## Dependencies And Integration Points
This supports metrics registry/source naming where repeated registration must not overwrite earlier objects.

## Risks
The key risk is suffix collision logic: names already containing `-N` must not be treated as free if already allocated. Ordering matters because the allocator tracks prior calls.

## Test Signals
Expected sequence is `foo`, `foo-1`, `foo-2`, `foo-1-1`, and `foo-2-1` depending on input order.

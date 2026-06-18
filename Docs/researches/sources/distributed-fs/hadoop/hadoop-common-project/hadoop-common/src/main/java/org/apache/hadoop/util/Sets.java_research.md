# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Sets.java

## Purpose
`Sets` is Hadoop's private replacement for the Guava `Sets` helpers commonly needed in core code: constructing mutable sets, set algebra, concurrent sets, and expected-size hash capacity calculation.

## Important APIs, Types, And Functions
Key APIs are `newHashSet`, varargs/iterable/iterator overloads, `newTreeSet`, `newHashSetWithExpectedSize`, `intersection`, `union`, `difference`, `differenceInTreeSets`, `symmetricDifference`, and `newConcurrentHashSet`. Internal helpers include `capacity`, `addAll`, and `cast`.

## Control Flow
Factory methods create mutable `HashSet` or `TreeSet` instances, optionally adding all inputs. Set algebra methods null-check inputs, copy into new sets, perform retain/add/remove operations, and return unmodifiable results. `capacity` mirrors Guava/JDK sizing logic and rejects negative expected sizes.

## State And Persistence
The class is stateless. Returned collections are in-memory only; algebra results are unmodifiable snapshots, not live views.

## Dependencies And Integration Points
It depends on Java collections and Hadoop annotations. It allows common code to avoid direct Guava `Sets` dependency.

## Risks
Javadocs contain a few inaccurate return descriptions inherited from copied text. Raw comparable bounds on `newTreeSet` are loose. Hash-based algebra has undefined ordering and depends on equality semantics; `differenceInTreeSets` changes ordering assumptions.

## Test Signals
Tests should verify all constructors, null rejection, negative expected size, expected capacity edge cases, unmodifiable algebra results, deterministic tree difference ordering, concurrent set null rejection, and duplicate handling.

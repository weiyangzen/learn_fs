# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SequentialNumber.java

## Purpose
`SequentialNumber` is a thread-safe abstract base for monotonically advanced ID generators backed by an `AtomicLong`.

## Important APIs, Types, And Functions
It implements `IdGenerator` and exposes `getCurrentValue`, `setCurrentValue`, `setIfGreater`, `nextValue`, `skipTo`, `equals`, and `hashCode`.

## Control Flow
`nextValue` atomically increments and returns the new value. `setIfGreater` CAS-loops until it either observes an existing value greater than or equal to the input or successfully swaps in the larger value. `skipTo` CAS-loops to a requested value but throws if it would move backwards. `setCurrentValue` is an unconditional store.

## State And Persistence
State is the atomic current value. There is no persistence; subclasses or callers must persist IDs if needed.

## Dependencies And Integration Points
It depends on `AtomicLong`, Hadoop annotations, and the `IdGenerator` contract. It is used by components needing simple sequential identifiers.

## Risks
`setCurrentValue` can move backwards and bypass monotonic guarantees. `equals` compares the `AtomicLong` object, not its contained value, so two generators with the same numeric value are not equal unless sharing the same atomic instance, which they never do in normal construction. Overflow is not checked.

## Test Signals
Tests should cover concurrent `nextValue`, `setIfGreater` races, `skipTo` backward rejection, unconditional reset behavior, overflow expectations, and equality/hash behavior.

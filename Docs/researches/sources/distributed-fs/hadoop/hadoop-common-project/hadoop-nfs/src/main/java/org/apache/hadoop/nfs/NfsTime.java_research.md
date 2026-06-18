# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/NfsTime.java

## Purpose
`NfsTime.java` encapsulates NFS seconds/nanoseconds timestamps and serializes them to XDR.

## Important APIs, Types, and Functions
- Constructors accept `(seconds, nseconds)`, another `NfsTime`, or milliseconds.
- `getSeconds()`, `getNseconds()`, and `getMilliSeconds()` expose time values.
- `serialize(XDR)` writes seconds and nanoseconds as two ints.
- `deserialize(XDR)` reads the same pair.
- `equals()` compares millisecond-equivalent values; `hashCode()` XORs seconds and nanoseconds.
- `toString()` formats a debug representation.

## Control Flow and State
Instances are immutable after construction. The milliseconds constructor splits milliseconds into seconds plus nanoseconds. XDR serialization is straightforward.

## Dependencies and Integration Points
`Nfs3FileAttributes` uses `NfsTime` for access, modification, and change times. `WccAttr` integration uses times derived from attributes.

## Risks and Edge Cases
The copy constructor sets `seconds = other.getNseconds()`, which appears suspicious because it likely intended `other.getSeconds()`. Equality compares only millisecond precision, while `hashCode()` includes raw nanoseconds, so two objects equal by milliseconds but with different sub-millisecond nanoseconds can have different hashes. Seconds are stored as `int`, limiting representable range.

## Test Signals
Protocol tests should verify XDR round-trip, millisecond conversion, equality/hash consistency, and copy-constructor correctness.

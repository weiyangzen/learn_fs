# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/options/JournalWriterOptions.java

## Purpose
`JournalWriterOptions` carries options for constructing journal writers.

## Important APIs, Types, And Functions
`defaults` returns a mutable options instance. Fields are next sequence number and primary flag, with fluent setters, getters, `equals`, `hashCode`, and `toString`.

## Control Flow, State, Dependencies, Risks, And Tests
The options guide concrete writer initialization, including first log sequence number and primary/standby behavior. They are not persisted themselves, but wrong values affect journal log persistence. Dependencies are Guava `MoreObjects` and `Objects`. Risks include default sequence zero mismatching journal conventions, mutable reuse across writers, and primary flag misconfiguration permitting or blocking writes incorrectly. Tests should cover defaults, fluent setters, equality/hash, toString, and writer behavior for sequence and primary settings.

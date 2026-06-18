# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/options/JournalReaderOptions.java

## Purpose
`JournalReaderOptions` carries options for constructing journal readers.

## Important APIs, Types, And Functions
`defaults` returns a new mutable options instance. Fields are next sequence number and primary-mode flag, with fluent setters, getters, `equals`, `hashCode`, and `toString`.

## Control Flow, State, Dependencies, Risks, And Tests
The options are in-memory construction parameters; they do not persist directly but control which persisted journal sequence is read and whether reader behavior is primary-aware. Dependencies are Guava `MoreObjects` and `Objects`. Risks include default `nextSequenceNumber` of zero if callers expect one, mutable options reuse, and equality relying on boxed `Objects.equal` for primitives. Tests should cover defaults, fluent setter chaining, equality/hash, toString, and concrete reader interpretation of primary mode.

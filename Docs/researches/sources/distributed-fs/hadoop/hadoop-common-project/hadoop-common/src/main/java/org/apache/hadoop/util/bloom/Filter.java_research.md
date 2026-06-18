# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/Filter.java

Purpose: `Filter` is the abstract Writable base for Hadoop Bloom-style filters, defining common metadata and bulk add operations.

Important APIs/types/functions: protected fields are `vectorSize`, `hash`, `nbHash`, and `hashType`. Abstract methods include `add`, `membershipTest`, `and`, `or`, `xor`, and `not`. Bulk `add` overloads accept `List<Key>`, `Collection<Key>`, and `Key[]`. `write` and `readFields` serialize a versioned header.

Control flow: constructors initialize hash metadata and create a `HashFunction`. Bulk add methods null-check the container and loop over keys. `readFields` supports old unversioned formats by treating a positive first int as `nbHash` and defaulting `hashType` to Jenkins; otherwise it requires current negative `VERSION`.

State and persistence behavior: inherited in-memory metadata drives hashing. Writable state persists header values and reconstructs `HashFunction` on read; subclasses append their own state.

Dependencies and integration points: depends on Hadoop `Writable`, Hadoop hash implementations, and `HashFunction`.

Risks: old-format compatibility must be preserved. Bulk add checks only the container, not individual null keys. `hashType` compatibility is not enforced by all subclasses' logical operations.

Test signals: tests should include header round trips, old-format reads, invalid version rejection, and bulk add null handling.

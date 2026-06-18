## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BlockLocation.java

Purpose: serializable data holder describing where a file block or erasure-coded block group resides: hosts, transfer names, topology paths, storage IDs/types, offset, length, and corruption state.

Important APIs and types: multiple constructors normalize null arrays to shared empty arrays and intern string arrays through `StringInterner`; getters and setters expose hosts, cached hosts, names, topology paths, storage IDs, storage types, offset, length, and corrupt flag; `isStriped()` defaults false; `toString()` prints offset, length, corruption, and hosts.

Control flow: constructors funnel into the full constructor. Setters repeat the null-to-empty and string-interning behavior. Copy constructor copies array references rather than deep-copying arrays.

State and persistence behavior: mutable in-memory metadata object with Java serialization UID. It does not persist block locations itself; namenode/filesystem clients populate it from storage metadata.

Dependencies and integration points: returned by `FileSystem` and `FileContext` block location APIs, embedded in `LocatedFileStatus`, and interpreted differently for replicated vs erasure-coded files.

Risks: arrays are exposed directly by getters and accepted directly by setters, so callers can mutate internal state. Copy construction is shallow. `isStriped()` is false unless subclasses override, so erasure-coded specializations must be used where needed.

Test signals: validate constructor null handling, string interning side effects, getter/setter mutation, shallow copy behavior, `toString()` with corrupt blocks, and compatibility with located status serialization.

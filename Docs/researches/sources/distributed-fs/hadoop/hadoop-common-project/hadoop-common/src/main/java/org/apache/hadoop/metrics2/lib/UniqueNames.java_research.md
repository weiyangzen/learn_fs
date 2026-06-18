<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/UniqueNames.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/UniqueNames.java

## Purpose
`UniqueNames` is a small private metrics2 helper that turns repeated metric or registry names into predictable unique names. The first caller receives the original name. Later collisions receive `name-1`, `name-2`, and so on.

## Important APIs and Types
The public surface is `uniqueName(String name)`. The nested `Count` type stores the original base name and the current suffix counter. A Guava `Joiner` formats suffixed names with `-`, and a mutable `Map<String, Count>` records every name already handed out.

## Control Flow
`uniqueName` is synchronized over the whole object. It checks whether the exact name is already in the map. If not, it inserts a counter and returns the name. If the name is present, it increments a counter and probes `name-N` until it finds an unused slot. Explicit user-provided names that already look suffixed are handled by probing until a free suffix exists.

## State and Persistence
All state is in memory and lifetime-bound to the `UniqueNames` instance. There is no expiry or reset API, so long-lived registries retain all allocated names.

## Dependencies and Integration Points
This class is private to metrics2 library code and supports registry/source implementations that need stable internal names. It depends only on Hadoop-shaded Guava and Hadoop audience annotations.

## Risks and Test Signals
The key risk is unbounded map growth if untrusted dynamic names are passed repeatedly. Tests should cover first-use identity, duplicate suffixes, explicit `foo-1` collisions, and concurrent callers receiving unique results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/UniqueNames.java -->

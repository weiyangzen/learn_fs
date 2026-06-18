# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/Edge.java

Purpose: immutable key representing an inode tree edge from a parent inode id to a child name.

Important APIs and types: constructor stores parent id and child name. `getId`, `getName`, `equals`, `hashCode`, and `toString` expose key behavior; `toString` formats `parent->name`.

Control flow: inode stores and lock managers can use `Edge` as a map/set key for child relationships and edge locks. Equality requires both parent id and child name to match.

State and persistence behavior: value object only. It represents persisted inode relationships but does not write them.

Dependencies and integration points: depends on Guava `Objects`. Integrates with inode tree edge lookup, edge locks, and child mapping code elsewhere in the meta package.

Risks: child name is not validated here; callers must ensure normalized names. Null names would be accepted by equality/hash code but likely invalid semantically.

Test signals: tests should cover equality, hash code, string formatting, and behavior as a map key.

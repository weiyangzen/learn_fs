# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/AccessPrivilege.java

## Purpose
`AccessPrivilege.java` defines the access outcomes for NFS export host matching.

## Important APIs, Types, and Functions
- Enum constants: `READ_ONLY`, `READ_WRITE`, and `NONE`.

## Control Flow and State
There is no behavior or mutable state. `NfsExports` assigns these values based on configured host matchers.

## Dependencies and Integration Points
The enum is used by `NfsExports` and downstream NFS server authorization checks to distinguish read-only, read-write, and denied clients.

## Risks and Edge Cases
Semantics depend on callers respecting `READ_ONLY` as a stronger denial of writes than `READ_WRITE`; the enum does not encode ordering itself.

## Test Signals
Behavior is covered indirectly through NFS export access tests outside this subset and through `NfsExports` logic.

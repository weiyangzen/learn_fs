# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/WithErasureCoding.java

## Purpose
Marker/extension interface for filesystems that expose erasure-coding policy queries and updates.

## Important APIs, Types, and Functions
getErasureCodingPolicyName(FileStatus) and setErasureCodingPolicy(Path,String).

## Control Flow
Implementations supply all behavior. Callers check filesystem instanceof WithErasureCoding before invoking.

## State and Persistence Behavior
No state in the interface. Implementations may mutate persistent filesystem metadata when setting policy.

## Dependencies and Integration Points
Integrates with FileSystem implementations and FileStatus-based EC reporting.

## Risks and Test Signals
Risks are null-on-error semantics for query hiding operational failures. Tests should verify supported/unsupported FS behavior and invalid policy/path errors.

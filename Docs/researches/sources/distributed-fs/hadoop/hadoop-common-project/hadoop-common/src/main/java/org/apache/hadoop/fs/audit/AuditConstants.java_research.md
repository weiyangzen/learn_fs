# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/AuditConstants.java

## Purpose
Central constant holder for audit parameter names and audit header fields.

## Important APIs, Types, and Functions
Constants include referrer origin, command, filesystem id, job/task/thread/process/principal/path/range/timestamp fields, and DELETE_KEYS_SIZE.

## Control Flow
No control flow; private constructor prevents instantiation.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
Used by audit span/context/header implementations, especially S3A audit integration.

## Risks and Test Signals
Risks are string drift breaking log/header parsers. Tests should treat constants as compatibility surface.

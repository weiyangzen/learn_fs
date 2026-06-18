<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/package-info.java

## Purpose
Marks the permission package private and unstable at package level.

## Important APIs, Types, And Functions
No runtime APIs; package annotations only.

## Control Flow
No control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Applies package metadata to Hadoop permission and ACL classes, although several individual classes expose stronger public/stable annotations.

## Risks
Package-level metadata can be broader than individual class annotations; callers should follow the class-level annotations for API stability.

## Test Signals
Annotation/documentation verification only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/package-info.java -->

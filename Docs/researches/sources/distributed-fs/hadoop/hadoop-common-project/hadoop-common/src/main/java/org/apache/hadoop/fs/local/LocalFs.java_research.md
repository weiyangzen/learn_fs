<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalFs.java

## Purpose
Implements the checksum-wrapped local `AbstractFileSystem` by extending `ChecksumFs` over `RawLocalFs`.

## Important APIs, Types, And Functions
The package-private constructors `LocalFs(Configuration)` and `LocalFs(URI, Configuration)` are the key entry points used by AFS creation.

## Control Flow
Construction creates a new `RawLocalFs` and passes it to `ChecksumFs`. The URI constructor delegates to the configuration constructor to satisfy `AbstractFileSystem#createFileSystem`.

## State And Persistence
State is inherited from `ChecksumFs` and the delegated raw filesystem. This file stores no additional fields.

## Dependencies And Integration Points
Integrates the newer `AbstractFileSystem` API with local checksum behavior and `RawLocalFs`.

## Risks
Constructors are package-private and assume creation through Hadoop filesystem factories. Behavior is mostly inherited, so regressions in `RawLocalFs` or `ChecksumFs` define the actual risk.

## Test Signals
Instantiate through `AbstractFileSystem`, create/read local files with checksum wrapper behavior, and verify URI construction works for `file://` local paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalFs.java -->

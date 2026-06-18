<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/Validate.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/Validate.java

## Purpose
Supplies prefetch-package validation helpers with consistent argument and state error messages.

## Important APIs, Types, And Functions
Provides null, positive, non-negative, required, valid, non-empty, exact-size, equality, multiple, greater, greater-or-equal, less-or-equal, range, path-exists/file/dir, and `checkState` helpers.

## Control Flow
All methods validate conditions and throw `IllegalArgumentException` through Hadoop `Preconditions.checkArgument`, except `checkState`, which throws `IllegalStateException`. Collection and iterable helpers reduce to length/existence checks.

## State And Persistence
No state. Constructor is private.

## Dependencies And Integration Points
Used throughout prefetch classes to keep parameter checking concise. Path helpers depend on `java.nio.file.Files`.

## Risks
`checkNotNullAndNotEmpty(Iterable)` calls `iterator().hasNext()` once; unusual iterables with side effects may be affected. Numeric helpers accept `long` but messages do not distinguish integer overflow at caller sites.

## Test Signals
Assert exception types/messages for each helper, especially range boundaries, empty arrays/iterables, path checks, and `checkState`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/Validate.java -->

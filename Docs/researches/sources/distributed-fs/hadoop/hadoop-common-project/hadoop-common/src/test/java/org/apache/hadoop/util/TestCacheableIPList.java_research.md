<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCacheableIPList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCacheableIPList.java

## Purpose

`TestCacheableIPList.java` verifies caching and refresh behavior for IP allow/deny lists backed by `FileBasedIPList`.

## Important APIs, Types, and Functions

Tests create `CacheableIPList(new FileBasedIPList("ips.txt"), 100)`, use `isIn`, `refresh`, and helpers from `TestFileBasedIPList`.

## Control Flow

The suite writes an initial IP list, checks membership, rewrites/removes the file, then either sleeps past the cache timeout or calls `refresh` explicitly before checking membership again. It covers both additions and removals.

## State and Persistence Behavior

State includes the cached delegate list, a short cache timeout, and the temporary `ips.txt` file in the working directory. Files are removed after tests.

## Dependencies and Integration Points

It integrates with `CacheableIPList`, `FileBasedIPList`, `IPList`, file helpers, and time-based invalidation.

## Risks and Edge Cases

Tests with `Thread.sleep(101)` are timing-sensitive. Shared filename `ips.txt` can conflict under parallel execution unless isolated.

## Test Signals

Signals include membership before/after timeout, membership after explicit refresh without waiting, and both addition/removal cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCacheableIPList.java -->

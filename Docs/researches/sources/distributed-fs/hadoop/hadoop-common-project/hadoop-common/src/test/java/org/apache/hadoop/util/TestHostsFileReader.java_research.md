<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestHostsFileReader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestHostsFileReader.java

## Purpose

`TestHostsFileReader.java` tests parsing, refresh, lazy refresh, and timeout metadata handling for include/exclude host files.

## Important APIs, Types, and Functions

It uses `HostsFileReader`, `HostsFileReader.HostDetails`, includes/excludes flat files, excludes XML file, `setIncludesFile`, `setExcludesFile`, `refresh`, `lazyRefresh`, `finishRefresh`, `getHosts`, `getExcludedHosts`, `getExcludedMap`, and `getLazyLoadedHostDetails`.

## Control Flow

Setup creates test files under `GenericTestUtils.getTestDir`; teardown deletes them. Tests write include/exclude entries, construct readers, assert parsed host counts, refresh to new file paths, handle nonexistent/null/comment-only files, parse spaces and tabs, parse XML-style decommission timeout values, perform lazy refresh into staged host details, then finish refresh to swap staged state.

## State and Persistence Behavior

Temporary include/exclude/XML files are written and deleted. Reader state includes active include/exclude maps, active file path strings, and optional lazy-loaded host details before `finishRefresh`.

## Dependencies and Integration Points

It integrates with `HostsFileReader`, Hadoop datanode host include/exclude semantics, `GenericTestUtils`, Java file writing/deletion, and JUnit 5.

## Risks and Edge Cases

Risks include stale lazy-refresh state, nonexistent file failures, whitespace parsing, comment-only files, XML timeout parsing, file path mutation during refresh, and shared temp directory cleanup.

## Test Signals

Signals include host/exclude counts and membership, exact timeout values including null and negative values, `NoSuchFileException` on missing files, lazy details before/after finish, and `IllegalStateException` when finishing without a lazy refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestHostsFileReader.java -->

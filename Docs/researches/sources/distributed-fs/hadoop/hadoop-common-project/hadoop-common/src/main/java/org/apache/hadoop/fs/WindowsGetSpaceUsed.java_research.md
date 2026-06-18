# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/WindowsGetSpaceUsed.java

## Purpose
Windows implementation of cached disk-usage accounting that avoids shelling out and uses DUHelper.

## Important APIs, Types, and Functions
Constructor accepts CachingGetSpaceUsed.Builder; refresh() sets used from DUHelper.getFolderUsage(getDirPath()).

## Control Flow
Superclass owns cache interval/jitter/initial value. refresh is invoked by the caching mechanism and atomically replaces the used counter.

## State and Persistence Behavior
Maintains only inherited cached used value. No persistence; it samples local filesystem usage.

## Dependencies and Integration Points
Depends on CachingGetSpaceUsed and DUHelper. Selected for Windows local space accounting.

## Risks and Test Signals
Risks are platform-specific path handling and DUHelper failures. Tests should cover builder initialization and refresh values for files/directories on Windows-like paths.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMappingWin.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMappingWin.c

## Purpose
`JniBasedUnixGroupsMappingWin.c` provides the Windows JNI implementation for Hadoop's group mapping class. It retrieves local Windows groups for a user and returns them as Java strings, while `anchorNative()` remains a no-op placeholder.

## Important APIs, Types, and Functions
JNI exports are `anchorNative()` and `getGroupsForUser()`. Internal `throw_ioexception()` formats Windows error messages. Static `emptyGroups` caches a global empty Java string array for error fallback. The file calls `GetLocalGroupsForUser()` and frees returned buffers with `NetApiBufferFree()`.

## Control Flow
`getGroupsForUser()` lazily creates `emptyGroups`, obtains the Java user string as UTF-16, calls the Windows helper to get local groups, allocates a Java string array sized to `ngroups`, iterates `LOCALGROUP_USERS_INFO_0` entries into Java strings, then releases buffers. On non-success return codes it throws an IOException and returns `emptyGroups`.

## State and Persistence
`emptyGroups` is a process-wide global reference. Group result buffers are per-call and freed before return.

## Dependencies and Integration Points
It depends on Windows APIs, Hadoop `winutils.h`, JNI, and the same Java `JniBasedUnixGroupsMapping` class used by Unix.

## Risks and Edge Cases
`FormatMessageA` is called with `buffer` rather than `&buffer` while using `FORMAT_MESSAGE_ALLOCATE_BUFFER`, so error message allocation may not work as intended. Returning `emptyGroups` after throwing an exception can be confusing to callers if they clear exceptions. Local references for group strings are not deleted inside the loop.

## Test Signals
Tests should cover users with zero/multiple local groups, invalid users, Windows error formatting, repeated calls reusing `emptyGroups`, and memory cleanup of NetAPI buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMappingWin.c -->

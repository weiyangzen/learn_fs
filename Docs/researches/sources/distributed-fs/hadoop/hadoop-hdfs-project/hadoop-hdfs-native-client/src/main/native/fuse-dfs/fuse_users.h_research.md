# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_users.h

## Purpose
Public identity lookup API for the FUSE client.

## Important APIs, Types, And Functions
Declares `getUsername`, `freeGroups`, `getGroup`, `getGroupUid`, `getGidUid`, and `getGroups`.

## Control Flow
No executable flow; callers receive heap-allocated strings or arrays that must be freed.

## State, Persistence, And Dependencies
Depends on POSIX uid/gid types and pthread-capable implementation. Ownership convention is documented in comments.

## Integration Points
Included by connection, chown, trash, and stat modules.

## Risks
Caller ownership is manual; missed frees leak, and using NULL returns without checks can crash.

## Test Signals
Unit tests around valid/invalid uid/gid and array cleanup would validate the API.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestNfs3Utils.java

## Purpose
`TestNfs3Utils` verifies access-right calculation from NFS file attributes, user id, group id, and auxiliary groups.

## Important APIs, Types, And Functions
The single test `testGetAccessRightsForUserGroup` mocks `Nfs3FileAttributes` and calls `Nfs3Utils.getAccessRightsForUserGroup` for regular files and directories.

## Control Flow
The test mutates mocked uid/gid/mode/type values across scenarios: owner mismatch under `0700`, group mismatch under `0070`, other permissions under `0007`, auxiliary-group read under `0440`, owner directory lookup under `0700`, denied group/auxiliary matches when mode lacks group bits, and directory lookup under `0711`.

## State And Persistence
There is no persistent state. Mockito stubs on a local mock object drive all cases.

## Dependencies And Integration Points
It supports `RpcProgramNfs3.access` and zero-count `read` permission checks, which call the same utility to translate POSIX mode bits into NFS ACCESS masks.

## Risks
Expected numeric masks are asserted directly with comments, which can obscure intent if constants change. The test does not cover symlink or special-file types.

## Test Signals
Passing confirms owner, group, auxiliary group, other, regular-file, and directory lookup/execute translations for common mode combinations.

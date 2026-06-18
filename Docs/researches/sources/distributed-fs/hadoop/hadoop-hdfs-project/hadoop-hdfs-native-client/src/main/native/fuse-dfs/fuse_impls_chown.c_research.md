# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_chown.c

## Purpose
Implements POSIX chown/chgrp using OS UID/GID name lookup and HDFS ownership APIs.

## Important APIs, Types, And Functions
`dfs_chown(const char *path, uid_t uid, gid_t gid)` uses `getUsername`, `getGroup`, `fuseConnectAsThreadUid`, and `hdfsChown`.

## Control Flow
If both uid and gid are `-1`, it returns success. Otherwise it resolves provided UID/GID to names, borrows an HDFS connection as the calling thread UID, calls `hdfsChown`, maps errno, releases connection, and frees lookup strings.

## State, Persistence, And Dependencies
Persists HDFS owner/group metadata. Depends on local passwd/group databases, global lookup mutexes in `fuse_users.c`, and libhdfs.

## Integration Points
Registered as `.chown`. Converts local numeric identities into HDFS string identities.

## Risks
Local OS names may not match HDFS users/groups. Protected paths are not checked. UID/GID are compared with `-1` despite unsigned platform typedefs, which is conventional but type-sensitive.

## Test Signals
Coverage should check owner/group updates, lookup failure mapping, and behavior under concurrent calls.

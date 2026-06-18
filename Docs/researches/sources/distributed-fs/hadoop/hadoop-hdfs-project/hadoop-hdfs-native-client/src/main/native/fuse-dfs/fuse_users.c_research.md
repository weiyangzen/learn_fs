# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_users.c

## Purpose
Thread-safe wrappers around local passwd/group lookups for FUSE identity mapping.

## Important APIs, Types, And Functions
Defines global mutexes `passwdstruct_mutex` and `groupstruct_mutex`. Exposes `getUsername`, `freeGroups`, `getGroup`, `getGroupUid`, `getGidUid`, and `getGroups`.

## Control Flow
Lookup functions lock the relevant mutex around non-reentrant libc calls, duplicate returned names, and unlock. `getGroups` has an inactive `GETGROUPS_T` branch; the active branch attempts to return the username and primary group.

## State, Persistence, And Dependencies
No persistent external state, but global mutexes serialize identity lookup. Depends on local `/etc/passwd`/NSS and `/etc/group`/NSS.

## Integration Points
Used by connection creation, chown, stat conversion, and trash path construction.

## Risks
The active `getGroups` branch writes to `groupnames[i]` while `groupnames` is still NULL, which is a latent crash if used. Local identity names may not match HDFS identities. Lock ordering must remain passwd then group when both are needed.

## Test Signals
Connection-as-UID, chown, stat owner mapping, and trash path tests validate these helpers; `getGroups` needs direct coverage because normal operation may not call it.

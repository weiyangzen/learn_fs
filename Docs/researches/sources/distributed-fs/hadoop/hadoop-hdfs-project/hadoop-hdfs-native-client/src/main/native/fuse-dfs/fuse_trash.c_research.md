# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_trash.c

## Purpose
Implements a C approximation of Hadoop Trash behavior for FUSE deletes.

## Important APIs, Types, And Functions
`hdfsDeleteWithTrash` is public. Internals include `get_parent_dir`, `get_trash_base`, and `move_to_trash`. Constants include `TRASH_RENAME_TRIES` and `ALREADY_IN_TRASH_ERR`.

## Control Flow
When trash is enabled, deletion tries to split the absolute path, construct `/user/<caller>/.Trash/Current<parent>/<name>`, create trash directories, choose a numbered target if needed, and rename the file there. If move fails or path is already in trash, fallback deletes recursively with `hdfsDelete`.

## State, Persistence, And Dependencies
Persists HDFS renames, trash directory creation, or final deletion. Depends on FUSE caller UID, local username lookup, libhdfs existence/create/rename/delete calls, and heap allocation via `strdup`/`asprintf`.

## Integration Points
Called by `dfs_unlink` and `dfs_rmdir` using the user-specific hdfsFS.

## Risks
Fallback after trash failure can permanently delete data. Trash path construction assumes `/user/<name>` convention. Existing trash collisions only try 99 suffixes. Parent split rejects root or malformed non-absolute paths.

## Test Signals
Tests should validate move-to-trash success, collision suffixing, already-in-trash deletion, and fallback delete behavior; current basic unlink/rmdir tests mostly cover deletion.

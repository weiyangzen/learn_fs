<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPFileSystem.java

## Purpose
Implements Hadoop `FileSystem` over SFTP using JSch channels and a small connection pool.

## Important APIs, Types, And Functions
Overrides `initialize`, `getUri`, `open`, `create`, `append`, `rename`, `delete`, `listStatus`, `mkdirs`, `getFileStatus`, working-directory/home methods, and `close`. Helpers handle URI-derived configuration, connect/disconnect, absolute path resolution, status lookup, permission conversion, recursive delete, mkdir recursion, and same-channel operations.

## Control Flow
Initialization extracts host, port, user, password, keyfile, and pool size from URI/config. Each public operation borrows a channel, performs SFTP calls, and returns the channel in `finally` or stream close. `open` resolves symlinks and wraps `SFTPInputStream`. `create` optionally deletes existing files, creates parent directories, and returns a stream whose close disconnects. Status lookup lists the parent directory and matches by filename; symlinks are resolved with `realpath` and restatted.

## State And Persistence
State includes the configured URI, connection pool, and closed flag. Remote filesystem metadata and data persist on the SFTP server; local state does not.

## Dependencies And Integration Points
Integrates Hadoop `FileSystem`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, and JSch `ChannelSftp`.

## Risks
Append is unsupported. Rename rejects existing destinations and claims same-directory limitations in constants, though implementation calls SFTP rename with paths. Recursive delete builds child paths from qualified statuses in a way that needs path coverage. `getHomeDirectory` returns null on errors. Permission/user/group are derived from numeric SFTP attrs. Stream users must close outputs before other APIs to avoid channel blocking.

## Test Signals
URI/config parsing, open/read/seek, create overwrite/non-overwrite, recursive mkdir/delete, directory listing, symlink status, rename failures, closed filesystem behavior, connection return on stream close, and auth/keyfile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPInputStream.java

## Purpose
Provides an `FSInputStream` wrapper around a JSch SFTP input stream with Hadoop seek and statistics behavior.

## Important APIs, Types, And Functions
Implements `seek`, `available`, `seekToNewSource`, `getPos`, `read`, `close`, and private `seekInternal`/`checkNotClosed`.

## Control Flow
Construction opens `channel.get(path)` and reads length via `lstat`. `seek` records the desired `nextPos`. `read` checks EOF, calls `seekInternal`, reads one byte, updates `pos` and `nextPos`, and increments statistics. Forward seek skips on the current stream; backward seek closes and reopens the remote stream, then skips to the target.

## State And Persistence
Holds the SFTP channel, path, wrapped stream, optional statistics, `closed`, actual `pos`, desired `nextPos`, and content length. Remote data is not modified.

## Dependencies And Integration Points
Created by `SFTPFileSystem.open` and closed by its wrapping `FSDataInputStream`, which returns the channel to the pool.

## Risks
`skip` may skip fewer bytes than requested; the code does not loop to reach `nextPos`. Backward seek reopens the file and may see changed remote content. The stats condition uses single `&`, which still works for booleans but does not short-circuit. Only single-byte `read()` is implemented here; bulk reads rely on `InputStream` defaults unless inherited behavior wraps it.

## Test Signals
Read EOF, negative seek, forward/backward seek with partial skip behavior, statistics increments, close idempotency, and remote file changes across backward seek.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPInputStream.java -->

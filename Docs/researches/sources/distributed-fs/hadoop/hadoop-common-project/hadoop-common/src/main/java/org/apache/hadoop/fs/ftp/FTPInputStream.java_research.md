# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPInputStream.java

## Purpose
FSInputStream wrapper around an FTP retrieveFileStream that tracks position/statistics and completes the pending FTP command on close.

## Important APIs, Types, and Functions
getPos(), read(), read(byte[],int,int), close(), seek/seekToNewSource unsupported, mark/reset unsupported.

## Control Flow
Constructor validates non-null stream and connected client. Reads delegate to wrappedStream and increment pos/statistics for positive reads. close is synchronized/idempotent, calls completePendingCommand(), logout(), disconnect(), then fails if command completion was not positive.

## State and Persistence Behavior
Stores wrapped InputStream, FTPClient, FileSystem.Statistics, closed flag, and byte position. Remote connection remains live until close.

## Dependencies and Integration Points
Created by FTPFileSystem.open(). Depends on Commons Net FTPClient and Hadoop FSInputStream statistics.

## Risks and Test Signals
Risks are transfer completion ordering, exceptions during logout/disconnect, double close behavior, and no seek support. Tests should cover byte counts, stats increments, read after close, and failed completePendingCommand.

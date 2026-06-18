# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FtpFs.java

## Purpose
DelegateToFileSystem adapter exposing ftp:// through the AbstractFileSystem/FileContext API.

## Important APIs, Types, and Functions
Constructor creates FTPFileSystem delegate; getUriDefaultPort(); getServerDefaults() overloads.

## Control Flow
Construction passes URI, FTPFileSystem, conf, scheme ftp, authority requirements, and default port. Server defaults are returned from FtpConfigKeys.

## State and Persistence Behavior
No own persistent state beyond DelegateToFileSystem base fields. Marked deprecated/evolving.

## Dependencies and Integration Points
Depends on FTPFileSystem, DelegateToFileSystem, AbstractFileSystem, FsConstants, FtpConfigKeys.

## Risks and Test Signals
Tests should verify FileContext ftp initialization, default port, and server defaults. Deprecated status means compatibility should be preserved.

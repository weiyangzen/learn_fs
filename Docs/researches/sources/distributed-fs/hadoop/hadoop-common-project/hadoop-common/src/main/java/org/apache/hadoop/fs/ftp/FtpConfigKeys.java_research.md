# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FtpConfigKeys.java

## Purpose
Configuration defaults for the FTP filesystem server defaults surface.

## Important APIs, Types, and Functions
Constants for block size, replication, buffer size, checksum, trash interval, encryption transfer default, and key provider URI; getServerDefaults().

## Control Flow
getServerDefaults creates FsServerDefaults using FTP-specific defaults and DataChecksum.Type.CRC32.

## State and Persistence Behavior
No mutable state.

## Dependencies and Integration Points
Depends on CommonConfigurationKeys, FsServerDefaults, ChecksumFileSystem, and DataChecksum. Used by FtpFs getServerDefaults.

## Risks and Test Signals
Risk is defaults diverging from FTPFileSystem assumptions. Tests should assert default values and checksum type.

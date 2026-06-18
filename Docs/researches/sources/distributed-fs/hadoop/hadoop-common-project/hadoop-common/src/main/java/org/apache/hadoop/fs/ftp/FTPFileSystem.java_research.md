# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPFileSystem.java

## Purpose
FileSystem implementation backed by Apache Commons Net FTPClient. It supports basic open, create, delete, listStatus, getFileStatus, mkdirs, and same-directory rename over FTP.

## Important APIs, Types, and Functions
Important APIs: initialize(), connect()/disconnect(), open(), create(), delete(), listStatus(), getFileStatus(), mkdirs(), rename(), getHomeDirectory(), getTransferMode(), setDataConnectionMode(), setTimeout().

## Control Flow
initialize resolves host/port/user/password from URI overriding configuration. Most operations open a new FTPClient, perform the command, then disconnect in finally. open/create are special: they change to the parent directory, obtain retrieveFileStream/storeFileStream, and return streams that hold the FTPClient until close; close must completePendingCommand then logout/disconnect. delete recurses when requested. getFileStatus lists the parent directory and converts FTPFile metadata to FileStatus. rename refuses missing sources, existing destinations, renames under self, and cross-directory moves.

## State and Persistence Behavior
The FileSystem itself stores only URI/config and no working directory; remote server state is persistent data/directories/files. Stream instances own live FTP connections until closed.

## Dependencies and Integration Points
Depends on commons-net FTPClient/FTPFile/FTPReply, Hadoop FileSystem, FileStatus, FsPermission/FsAction, IOUtils, NetUtils, and configuration keys. FtpFs delegates to it through DelegateToFileSystem.

## Risks and Test Signals
Risks are connection leaks if streams are not closed, blocking FTP commands while a transfer stream is open, path qualification bugs, recursive delete path construction, weak credential parsing with colon characters, and same-directory rename limitations. Tests should use a controllable FTP server to cover passive/active modes, transfer modes, create overwrite, failed preliminary replies, close completion failures, recursive delete, root status, and rename edge cases.

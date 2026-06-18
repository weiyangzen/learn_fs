# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/ftp/FtpTestServer.java

## Purpose
`FtpTestServer` is a small embedded Apache FTPServer wrapper used by FTP filesystem tests.

## Important APIs, Types, And Functions
Constructor accepts a root `Path`, creates a `UserManager`, builds an `FtpServer`, and stores fields. Public methods are `start()`, `getFtpRoot()`, `getPort()`, `stop()`, and `addUser(String, String, Authority...)`. `createServerFactory()` configures a default listener on port 0.

## Control Flow
Construction creates the server but does not start it. `start()` starts the server, extracts the assigned listener port from `DefaultFtpServer`, and returns `this`. `addUser()` creates a per-user home directory under the FTP root, sets credentials/authorities, saves it in the manager, and returns the `BaseUser`. `stop()` is idempotent around `server.isStopped()`.

## State And Persistence
State includes selected port, FTP root path, user manager, and server. Persistent effects are per-user home directories and files created through FTP tests.

## Dependencies And Integration Points
It depends on Apache FTPServer factories, listeners, user manager, `BaseUser`, and ftplet authorities. `TestFTPFileSystem` uses it for isolated tests.

## Risks
User home creation can fail if the root is missing or permissions are wrong. Server lifecycle leaks can leave bound ports or temp directories.

## Test Signals
Signals are successful port assignment, user creation with correct authorities, and server stop during teardown.

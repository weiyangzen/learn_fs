# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/sftp/SFTPContract.java

## Purpose
`SFTPContract` provides an embedded SFTP server-backed filesystem contract for tests, avoiding dependence on an external SFTP service.

## Important APIs, Types, And Functions
It extends `AbstractFSContract`, loads `contract/sftp.xml`, uses `TEST_URI = sftp://user:password@localhost`, and implements `init()`, `teardown()`, `getTestFileSystem()`, `getScheme()`, and `getTestPath()`.

## Control Flow
`init()` creates an Apache SSHD `SshServer`, binds port 0, configures generated host keys, password auth for `user/password`, installs an SFTP subsystem, starts the server, then writes SFTP FS implementation, port, and cache-disable settings into the configuration. `getTestFileSystem()` resolves the test URI through that configuration. `teardown()` stops the server.

## State And Persistence
The contract stores `conf`, `testDataDir`, and the live `SshServer`. Files are persisted under the server's backing local directory through SFTP during a test.

## Dependencies And Integration Points
It integrates `SFTPFileSystem` with Apache SSHD server/auth/subsystem classes and contract tests such as seek.

## Risks
Server lifecycle must be balanced or tests leak ports/threads. Using a fixed localhost URI with a configured port relies on `fs.sftp.host.port` and disabled cache to avoid stale connections.

## Test Signals
Signals are successful SSHD startup on an ephemeral port, authenticated SFTP FS resolution, and clean server stop in teardown.

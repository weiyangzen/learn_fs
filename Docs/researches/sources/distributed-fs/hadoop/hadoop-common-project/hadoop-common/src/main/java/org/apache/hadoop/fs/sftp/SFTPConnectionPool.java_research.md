<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPConnectionPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPConnectionPool.java

## Purpose
Maintains reusable JSch SFTP channels keyed by host, port, and user for `SFTPFileSystem`.

## Important APIs, Types, And Functions
`connect`, `disconnect`, `shutdown`, `getFromPool`, `returnToPool`, connection count accessors, and nested `ConnectionInfo` define the pool. `setMaxConnection` changes the threshold for keeping idle channels.

## Control Flow
`connect` first tries an idle channel. If none is connected, it creates a JSch session, optionally adds an identity file, fills missing user/password defaults, disables strict host key checking, connects a session/channel, and records it. `disconnect` closes the channel/session only when live connections exceed `maxConnection`; otherwise it returns the channel to the idle map. `shutdown` sets max to zero and disconnects every known channel.

## State And Persistence
State includes `maxConnection`, `liveConnectionCount`, `idleConnections`, and `con2infoMap`. Connections are live network/session resources, not persistent state.

## Dependencies And Integration Points
Used exclusively by `SFTPFileSystem`. Depends on JSch `Session`/`ChannelSftp`, Hadoop `StringUtils`, and SLF4J.

## Risks
Host key checking is disabled, which is a security risk. `getFromPool` removes the entire idle set for a `ConnectionInfo` when taking one channel, potentially losing references to other idle channels. A disconnected borrowed channel path removes `null` after assigning `channel = null`, leaving stale map entries. Count accessors are not synchronized.

## Test Signals
Pool reuse, max-connection eviction, shutdown idempotency, disconnected idle channels, key/password auth paths, host/user case-insensitive keys, and stale idle map behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPConnectionPool.java -->

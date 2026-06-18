# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestHostRestrictingAuthorizationFilterHandler.java

## Purpose

`TestHostRestrictingAuthorizationFilterHandler` validates the Netty wrapper around `HostRestrictingAuthorizationFilter` for DataNode WebHDFS requests. It checks default reject-all behavior, allowed GET request pass-through, channel reuse, multi-channel sharing of one filter instance, and unconditional allowance for `GETFILECHECKSUM`.

## Important APIs and types

- `HostRestrictingAuthorizationFilterHandler.initializeState(Configuration)` builds the underlying ACL filter.
- Configuration key is the HDFS-prefixed restriction key from `HostRestrictingAuthorizationFilter`.
- Netty `EmbeddedChannel`, `DefaultFullHttpRequest`, and `DefaultHttpResponse` simulate inbound HTTP processing.
- `WebHdfsFileSystem.PATH_PREFIX` provides the WebHDFS URI prefix.
- `CustomEmbeddedChannel.remoteAddress0` supplies deterministic client IPs.

## Control flow

`testRejectAll` installs a default handler without ACL rules, sends a WebHDFS `OPEN` request, expects `writeInbound` false, polls a forbidden response, and verifies the channel closes. `testMultipleAcceptedGETsOneChannel` configures `*,*,/allowed`, sends three allowed `OPEN` requests through one channel, and expects all to pass inbound. `testMultipleChannels` shares one initialized filter across three channels with different remote addresses and verifies closing one channel does not affect another. `testAcceptGETFILECHECKSUM` sends a checksum request through the default handler and expects it to pass.

## State and persistence behavior

All state is in-memory Netty channel state and filter configuration. No server socket or cluster starts. The shared filter instance carries ACL state but should not carry channel-specific state.

## Dependencies and integration points

This file integrates DataNode Netty WebHDFS request handling, host/path authorization rules, remote-address extraction, and special-casing of checksum operations.

## Risks and edge cases

- ACL coverage is minimal: one allow rule and the no-rule default.
- It does not test non-GET methods, proxy headers, IPv6, hostnames, or malformed paths.
- Rejected request body/resource release behavior is not asserted.
- The checksum allowance is tested independent of path ACLs, which is intentional but security-sensitive.

## Test signals

Strong signals are forbidden response status and channel close on reject, repeated accepted requests on one channel, shared filter behavior across channels, and explicit checksum pass-through.

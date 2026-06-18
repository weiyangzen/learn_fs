# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestDoAsEffectiveUser.java

Purpose: Integration tests for proxy-user/doAs behavior over Hadoop protobuf RPC, including IP/group authorization and token-auth interactions.

Important APIs/types/functions: `UserGroupInformation.createProxyUser`, `createProxyUserForTesting`, `doAs`, `ProxyUsers.refreshSuperUserGroupsConfiguration`, `DefaultImpersonationProvider`, `RPC.setProtocolEngine`, `ProtobufRpcEngine2`, `TestRpcBase` server/client helpers, `SecurityUtil.setAuthenticationMethod`, and test tokens.

Control flow: setup resets UGI config and proxy-user conf. Helper `configureSuperUserIPAddresses` whitelists local interface addresses. Tests assert local `doAs` string form, successful remote real/proxy calls, expected failures for bad/missing IP or group config, and token-auth cases where the server reports token owner/renewer rather than proxy user.

State and persistence: global UGI configuration, global proxy-user configuration, live in-process RPC servers, client field, authentication method in conf, and token service address.

Dependencies/integration points: Hadoop IPC, protobuf RPC engine, proxy-user authorization, network interfaces, token secret manager.

Risks: live networking and 4-second timeouts can be flaky; local IP enumeration is environment-dependent; several failure tests catch any exception and print stack traces, so they mainly assert that an RPC failed.

Test signals: verifies proxy identity propagation to server, enforcement of superuser host/group policy, and precedence of token identity during RPC authentication.

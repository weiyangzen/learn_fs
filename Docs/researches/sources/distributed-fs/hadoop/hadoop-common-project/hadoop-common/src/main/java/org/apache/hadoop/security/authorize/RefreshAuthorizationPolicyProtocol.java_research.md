# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/RefreshAuthorizationPolicyProtocol.java

## Purpose

`RefreshAuthorizationPolicyProtocol` is the RPC protocol for refreshing service-level authorization policy in a running Hadoop daemon.

## Important APIs, Types, and Functions

It defines protocol `versionID = 1L` and idempotent `refreshServiceAcl()`. `@KerberosInfo` points at the Hadoop service principal key.

## Control Flow

Implementing daemons receive the RPC and reload authorization ACL policy, typically through `ServiceAuthorizationManager.refresh`.

## State and Persistence Behavior

The interface owns no state. Its implementations mutate daemon-local authorization-manager state from configuration/policy resources.

## Dependencies and Integration Points

It integrates with Hadoop IPC, Kerberos principal discovery, protobuf translators in `protocolPB`, and admin refresh commands.

## Risks and Edge Cases

Failed reloads should surface as `IOException`; because the method is idempotent, clients may retry. Incorrect Kerberos principal configuration can prevent the refresh RPC from being invoked.

## Test Signals

Tests should cover protobuf translator invocation, method support lookup, Kerberos annotation metadata, successful reload, and propagation of implementation `IOException`.

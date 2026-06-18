# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/PolicyProvider.java

## Purpose

`PolicyProvider` supplies the set of Hadoop RPC services and protocol classes that participate in service-level authorization.

## Important APIs, Types, and Functions

It defines `POLICY_PROVIDER_CONFIG`, `DEFAULT_POLICY_PROVIDER`, and abstract `getServices()`. Each returned `Service` ties a configuration ACL key to a protocol class.

## Control Flow

There is no runtime algorithm in this class. `ServiceAuthorizationManager.refreshWithLoadedConfiguration` calls `getServices` and materializes ACL and host rules for each service.

## State and Persistence Behavior

The abstract class is stateless; persistence lives in Hadoop configuration resources such as `hadoop-policy.xml`.

## Dependencies and Integration Points

It integrates directly with `ServiceAuthorizationManager` and the configured policy provider class for HDFS, MapReduce, and related services.

## Risks and Edge Cases

A provider returning null or omitting a service leaves that protocol unknown to service authorization. Mis-keyed service definitions silently fall back to default ACLs/hosts.

## Test Signals

Tests should assert provider service arrays are complete and that service keys map to the intended protocol ACLs after authorization-manager refresh.

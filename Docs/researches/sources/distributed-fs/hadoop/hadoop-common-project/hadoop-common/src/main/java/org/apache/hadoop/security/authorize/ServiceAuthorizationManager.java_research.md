# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ServiceAuthorizationManager.java

## Purpose

`ServiceAuthorizationManager` enforces service-level authorization for Hadoop RPC protocols. It checks allowed/blocked user ACLs, Kerberos client principal constraints, and allowed/blocked client host lists.

## Important APIs, Types, and Functions

Primary APIs are `authorize(UserGroupInformation, Class<?>, Configuration, InetAddress)`, `refresh(Configuration, PolicyProvider)`, and `refreshWithLoadedConfiguration`. It keeps `protocolToAcls` and `protocolToMachineLists` as volatile identity maps, defines suffixes `.blocked` and `.hosts`, and provides testing accessors for loaded ACLs/hosts.

## Control Flow

`refresh` copies configuration, loads the policy resource named by system property `hadoop.policy.file` or `hadoop-policy.xml`, then delegates to `refreshWithLoadedConfiguration`. Refresh builds fresh identity maps from provider services, using default allow/block ACLs and default allow/block machine lists when service-specific keys are absent, then atomically flips the volatile references. `authorize` fails unknown protocols, resolves the client principal when security is enabled, denies mismatched principal, denied allowed ACL, matched blocked ACL, non-included host, or matched blocked host, and logs audit success/failure.

## State and Persistence Behavior

Authorization state is held in volatile maps for lock-free reads and atomic refresh replacement. Policy persistence lives in Hadoop XML configuration and system property-selected policy files.

## Dependencies and Integration Points

It depends on `AccessControlList`, `MachineList`, `SecurityUtil`, `UserGroupInformation`, `CommonConfigurationKeys`, `PolicyProvider`, `Service`, and audit logging. It is invoked by Hadoop RPC server paths before dispatching protocol calls.

## Risks and Edge Cases

Identity maps require the exact protocol `Class<?>` object used during refresh. Defaults can unintentionally allow all users/hosts if policy keys are absent. Host authorization is skipped when `addr` is null. Principal resolution failures are converted to authorization failures.

## Test Signals

Tests should cover unknown protocols, allowed and blocked ACL precedence, allowed and blocked host precedence, security-enabled principal mismatch, null-address behavior, policy-file refresh, volatile map replacement, and default policy fallbacks.

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestServiceAuthorization.java

Purpose: validates `ServiceAuthorizationManager` ACL and machine-list authorization for RPC protocols, including default ACLs, blocked ACLs, default blocked ACLs, host allow lists, host block lists, and client-principal lookup in unsecure mode.

Important APIs and types: `ServiceAuthorizationManager`, `PolicyProvider`, `Service`, `AccessControlList`, `UserGroupInformation`, `SecurityUtil.setSecurityInfoProviders`, custom `SecurityInfo`, `KerberosInfo`, `TokenInfo`, `TestRPC.TestProtocol`, `Configuration`, `InetAddress`, and `CommonConfigurationKeys`.

Control flow: a test policy provider maps two protocol interfaces to ACL config keys. A custom security info provider returns a client principal key to ensure authorization works in unsecure mode when client principal metadata exists. ACL tests refresh the manager with different config combinations and authorize a UGI against protocol classes. They verify explicit protocol ACLs override defaults, missing ACLs use wildcard or default ACLs, blocked ACLs deny by user or group, empty blocked ACL resets denial, and default blocked ACL applies to protocols without explicit blocked ACL. Machine-list tests perform the same pattern for allowed hosts, default allowed hosts with CIDR/exact IPs, blocked hosts, and default blocked hosts.

State and persistence: in-memory manager/config only, but `SecurityUtil.setSecurityInfoProviders` mutates static security info providers and is not restored in this file.

Dependencies and integration points: integrates RPC protocol policy metadata, ACL parsing, machine list/CIDR matching, security info principal lookup, and UGI group membership.

Risks: static `SecurityUtil` provider mutation can leak. Tests rely on concrete IPs and exact default config keys. They mostly assert success/failure by catching exceptions, not exception messages.

Test signals: strong authorization matrix coverage for service ACL precedence, blocked ACL precedence, machine allow/block lists, and protocol-specific versus default policy behavior.

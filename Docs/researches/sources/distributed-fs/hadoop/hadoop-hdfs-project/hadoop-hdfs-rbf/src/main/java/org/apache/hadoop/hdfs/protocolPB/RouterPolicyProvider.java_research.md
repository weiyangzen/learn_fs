# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterPolicyProvider.java

Purpose: RBF policy provider that extends HDFS service authorization with Router-specific protocol ACLs.

Important APIs and types: extends `HDFSPolicyProvider`; defines `RBF_SERVICES` with `CommonConfigurationKeys.SECURITY_ROUTER_ADMIN_PROTOCOL_ACL` mapped to `RouterAdminProtocol`; constructor merges `super.getServices()` with Router services; `getServices()` returns a defensive copy.

Control flow: construction eagerly builds the combined service array. Calls to `getServices()` do not expose the internal array.

State and persistence: holds an immutable-by-convention `Service[]` for process lifetime. Actual ACL values are read elsewhere from Hadoop configuration.

Dependencies and integration points: used by Hadoop service authorization to recognize Router admin protocol permissions alongside normal HDFS protocol permissions.

Risks: missing Router protocols here would bypass intended service-level ACL configuration. Duplicate or stale service entries can confuse authorization diagnostics. Tests should assert the provider includes all parent HDFS services plus the Router admin ACL service and that returned arrays are defensive copies.

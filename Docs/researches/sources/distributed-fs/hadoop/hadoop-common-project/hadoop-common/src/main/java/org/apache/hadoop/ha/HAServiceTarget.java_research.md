# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceTarget.java

Purpose: Abstracts a concrete HA service endpoint for admin, health monitor, failover, ZKFC, and fencing code.

Important APIs and types: Subclasses implement `getAddress()`, `getZKFCAddress()`, `getFencer()`, and `checkFencingConfigured()`. Optional hooks include `getHealthMonitorAddress()`, `isAutoFailoverEnabled()`, `supportObserver()`, and `addFencingParameters()`. Proxy factories include `getProxy()`, `getHealthMonitorProxy()`, and `getZKFCProxy()`. It also stores `transitionTargetHAStatus` for fencing context.

Control flow: Controllers resolve targets, create protocol translators using configured socket factories and IPC retries, pass target metadata to fencers, and optionally use a dedicated health-monitor address. ZKFC proxies are used for graceful failover coordination.

State and persistence: Holds only the intended transition target state. Endpoint addresses and fencer configuration are supplied by subclasses. No persistence in this base class.

Dependencies and integration points: Uses `HAServiceProtocolClientSideTranslatorPB`, `ZKFCProtocolClientSideTranslatorPB`, `NetUtils`, Hadoop IPC retry keys, and fencer parameter maps.

Risks: Incorrect addresses route control-plane RPCs to the wrong service. Fencing parameter keys feed shell environments and scripts. `transitionTargetHAStatus` is mutable and must be set consistently when source/destination-specific fencing commands are used.

Test signals: Dummy HA service tests, health monitor dedicated-address tests, admin/failover tests, and fencer environment tests validate target behavior.

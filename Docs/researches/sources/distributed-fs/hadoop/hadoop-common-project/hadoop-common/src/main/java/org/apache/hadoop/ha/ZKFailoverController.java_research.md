# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ZKFailoverController.java

Purpose: Abstract base for a service-specific ZooKeeper Failover Controller. It connects health monitoring, ZooKeeper election, local HA transitions, fencing, RPC admin control, and graceful failover orchestration.

Important APIs and types: Subclasses implement target serialization, login, RPC admin access, bind address, policy provider, peer target list, SSL flag, and ZK scope. Public API includes `run()`, `getLocalTarget()`, and test hooks. Internal major methods are `initZK()`, `initHM()`, `initRPC()`, `becomeActive()`, `becomeStandby()`, `fenceOldActive()`, `cedeActive()`, `doGracefulFailover()`, `recheckElectability()`, and `verifyChangedServiceState()`.

Control flow: `run()` verifies auto failover, logs in, initializes ZooKeeper, handles optional `-formatZK`, checks parent znode and fencing, starts RPC and health monitor, then waits until fatal error. Health callbacks join or quit election based on health. Elector callbacks transition the local service active/standby or fence an old active. Graceful failover asks non-target peers and the old active to cede, waits for a normal active attempt, then lets peers rejoin.

State and persistence: Tracks configuration, local target, health monitor, elector, RPC server, last health state, volatile service state, fatal error, cede delay, delayed recheck executor, and last active-attempt record. Persistent coordination state is stored in ZooKeeper by `ActiveStandbyElector`.

Dependencies and integration points: Central integration point for `HealthMonitor`, `ActiveStandbyElector`, `FailoverController`, `ZKFCRpcServer`, `ZKFCProtocol`, `HAServiceProtocol`, security login, ACL/auth parsing, credential-provider exclusion, and service-specific subclasses such as HDFS ZKFC.

Risks: Safety relies on correct lock ordering (`elector` then ZKFC), health-state accuracy, service-state mismatch detection, fencing configuration, and ZooKeeper session behavior. Graceful failover has timing windows around cede duration, active-attempt wait, and old-active rejoin. Fatal errors stop the controller.

Test signals: `TestZKFailoverController`, stress tests, real-ZK elector tests, mini-cluster HA failover tests, service-state mismatch tests, formatZK tests, and fencing failure tests cover most control paths.

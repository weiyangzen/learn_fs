# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HealthMonitor.java

Purpose: Runs a daemon loop that connects to an HA service, periodically checks service status and health, and notifies callbacks when health or service state changes.

Important APIs and types: `HealthMonitor` exposes `addCallback()`, `addServiceStateCallback()`, `shutdown()`, `getProxy()`, `start()`, `join()`, and test-visible health state. Enums include `State` values `INITIALIZING`, `SERVICE_NOT_RESPONDING`, `SERVICE_HEALTHY`, `SERVICE_UNHEALTHY`, and `HEALTH_MONITOR_FAILED`. Callback interfaces are `Callback` and `ServiceStateCallback`.

Control flow: `MonitorDaemon.work()` loops until shutdown, first `loopUntilConnected()` with retry sleep, then `doHealthChecks()`. Each health iteration calls `getServiceStatus()` and `monitorHealth()`. Domain health failures enter `SERVICE_UNHEALTHY`; transport failures stop the proxy, enter `SERVICE_NOT_RESPONDING`, sleep, and reconnect. Uncaught daemon errors enter `HEALTH_MONITOR_FAILED`.

State and persistence: Holds timing/retry config, volatile `shouldRun`, current proxy, current health state, last service status, and synchronized callback lists. No persisted state.

Dependencies and integration points: Used by `ZKFailoverController` to join or quit election based on local health and observed service state. Depends on `HAServiceTarget`, `HAServiceProtocol`, Hadoop IPC `RPC.stopProxy()`, `RemoteException`, and HA health configuration keys.

Risks: Callbacks run on the monitor thread, so slow or throwing callbacks delay checks or kill monitoring. Transport/health exception classification must unwrap remote health failures correctly. Aggressive intervals can overload services; slow intervals delay failover.

Test signals: `TestHealthMonitor` and `TestHealthMonitorWithDedicatedHealthAddress` cover connection retry, state transitions, unhealthy versus not responding, callback ordering, shutdown, and dedicated health RPC address.

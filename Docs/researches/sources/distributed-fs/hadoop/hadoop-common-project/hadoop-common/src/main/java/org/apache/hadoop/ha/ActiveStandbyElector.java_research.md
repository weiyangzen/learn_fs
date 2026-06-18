# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ActiveStandbyElector.java

Purpose: Implements a ZooKeeper-backed active/standby leader election library. It uses one ephemeral lock znode to elect the active service and a persistent breadcrumb znode to identify the last active for fencing before a new active proceeds.

Important APIs and types: Public surface includes `ActiveStandbyElector`, `ActiveStandbyElectorCallback`, constructors, `joinElection()`, `quitElection()`, `parentZNodeExists()`, `ensureParentZNode()`, `clearParentZNode()`, `getActiveData()`, `terminateConnection()`, `getHAZookeeperConnectionState()`, and test hooks. Internal state enums are `State` and `ConnectionState`; callback processing implements ZooKeeper `StatCallback` and `StringCallback`.

Control flow: `joinElection()` copies app data and asynchronously creates the lock znode. A successful create fences any breadcrumb owner, writes/updates the breadcrumb, calls `appClient.becomeActive()`, and monitors the lock. `NODEEXISTS` means standby plus a watch on the active lock. Deletion or session changes trigger neutral mode, session recreation, and rejoining if appropriate. ZooKeeper operations are retried for connection loss and operation timeout up to `maxRetryNum`.

State and persistence: Local synchronized state tracks ZooKeeper client, watcher, election desire, app data, retry counts, monitor request status, and current ACTIVE/STANDBY/NEUTRAL/INIT state. Persistent ZooKeeper state is the parent znode, ephemeral `ActiveStandbyElectorLock`, and persistent `ActiveBreadCrumb`.

Dependencies and integration points: Used by `ZKFailoverController`. Depends on ZooKeeper, ACL/auth configuration, Hadoop `SecurityUtil` SSL/TLS setup, `ZKUtil`, and the callback's transition/fencing implementation.

Risks: Split-brain avoidance depends on session semantics, breadcrumb writes, stale-client filtering, callback speed, and application fencing correctness. Lock ordering and synchronized callbacks are sensitive. Short session timeouts can cause flapping, while stale breadcrumbs can force fencing after graceful-release failures.

Test signals: `TestActiveStandbyElector`, `TestActiveStandbyElectorRealZK`, ZKFC integration tests, session-expiry tests, ACL/auth tests, retry-path tests, and fencing/breadcrumb tests validate this file.

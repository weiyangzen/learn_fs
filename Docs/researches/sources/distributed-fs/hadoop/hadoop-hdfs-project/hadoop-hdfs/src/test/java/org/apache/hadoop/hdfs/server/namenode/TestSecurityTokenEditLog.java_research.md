# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecurityTokenEditLog.java

Purpose: Tests edit-log recording and replay for delegation token operations under concurrency and token expiration. It validates that get, renew, and cancel token operations are durable and that implicit expiration cancellation logs while holding the correct NameNode lock.

Important APIs and functions: Static setup disables fsync for speed. `Transactions` repeatedly calls `FSNamesystem.getDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`, and `editLog.logSync`. `testEditLog()` starts a MiniDFSCluster with delegation tokens always enabled, launches 100 `SubjectInheritingThread`s, closes the edit log, and reloads edits with `FSEditLogLoader`. `testEditsForCancelOnTokenExpire()` uses mocked `FSImage`/`FSEditLog` and a real `FSNamesystem`.

Control flow: The concurrency test writes `NUM_THREADS * NUM_TRANSACTIONS * 3` token transactions plus key and segment transactions, then verifies each finalized edits file loads exactly the expected count. The expiration test creates two tokens, renews one halfway, forces secret-manager scans by stop/start, and verifies implicit cancels are logged only after each token expires.

State and persistence behavior: Persistent state is the NameNode edit log containing delegation token operations and secret-manager master keys. The expiration test checks lock state during logging: read lock held, write lock not held.

Dependencies and integration points: Integrates `DelegationTokenSecretManager`, `DelegationTokenIdentifier`, `FSEditLog`, `FSEditLogLoader`, storage directories, UGI, and FSNamesystem locking through `RwLockMode`.

Risks: High concurrency can expose edit-log corruption or transaction count mismatches. Timing around token expiration uses sleeps and forced scanner restarts. Locking assertions protect against unsafe edit-log rolling interactions.

Test signals: Signals include successful edit-log replay with expected transaction count for every edits directory, exact Mockito verification of get/renew/cancel calls, and read-lock/no-write-lock assertion during expiration cancel logging.

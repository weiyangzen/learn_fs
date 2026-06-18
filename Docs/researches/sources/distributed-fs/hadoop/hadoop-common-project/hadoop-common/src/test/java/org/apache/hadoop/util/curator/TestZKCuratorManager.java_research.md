# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/curator/TestZKCuratorManager.java

Purpose: Integration tests for non-TLS `ZKCuratorManager` operations and its ZooKeeper factory configuration. It covers znode CRUD, child listing, string data, safe transactions, JAAS configuration, and Curator builder integration.

Important APIs/types/functions: `setup()` starts a Curator `TestingServer`, creates `ZKCuratorManager`, and calls `start(zkHostPort)`. Tests invoke `exists()`, `create()`, `delete()`, `setData()`, `getData()`, `getStringData()`, `getChildren()`, `createTransaction()`, and `ZKCuratorManager.HadoopZookeeperFactory`. `validateJaasConfiguration()` checks `ZKClientConfig.LOGIN_CONTEXT_NAME_KEY` and JAAS `AppConfigurationEntry` options.

Control flow: CRUD tests create znodes, mutate byte/string payloads, and assert existence/children counts. Transaction tests create a `SafeTransaction`, queue create/set/delete operations, assert no pre-commit changes, then commit and verify atomic effects. JAAS tests construct multiple factories with different principals/keytabs, create ZooKeeper clients, and verify the selected login context; one branch sets a global JAAS configuration and login-context system property to confirm it overrides factory principals. Curator factory test builds a `CuratorFramework` with the Hadoop factory and validates the resulting client.

State and persistence behavior: A live in-process ZooKeeper server persists znodes for each test until teardown. JAAS configuration and `ZKClientConfig.LOGIN_CONTEXT_NAME_KEY` are process-global; the test clears the property in a `finally` block for the global override path. Transaction state is local until `commit()`.

Dependencies and integration points: Depends on Apache Curator framework/test, ZooKeeper, Hadoop `Configuration`, `CommonConfigurationKeys`, `SecurityUtil`, `JaasConfiguration`, and `ZKUtil` ACL parsing. It validates coordination-service integration used by Hadoop HA and service fencing paths.

Risks: In-process ZooKeeper tests can be flaky if ports or background server cleanup fail. Process-global JAAS state is a cross-test hazard. Children-count assertions include ZooKeeper's default root child, so Curator/ZooKeeper version behavior can affect expected counts.

Test signals: Existence/data assertions, children-count changes, pre/post-commit transaction visibility, matching byte arrays, JAAS principal/keytab values, and Curator-created ZooKeeper config are key signals.

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestCuratorService.java

Purpose: integration-style tests for low-level ZooKeeper/Curator wrapper operations in `CuratorService`.

Important APIs and functions: fixture creates a `CuratorService` connected to the micro ZooKeeper. Tests cover `zkList`, existence checks, `zkPathMustExist`, path creation with persistent and ephemeral modes, `maybeCreate`, recursive and nonrecursive delete, background delete callbacks, create, duplicate create, update, and use of a `MicroZookeeperService` as binding source.

Control flow: each test starts a fresh curator and ensures root exists with world read/write ACL. Delete tests distinguish leaf deletion, nonrecursive failure on children, and recursive success. Update tests allow setting data on directory nodes, including nodes with children.

State and persistence: all mutations occur in the shared test ZooKeeper namespace. Root ACLs are permissive test ACLs. Service is stopped after each test.

Dependencies and integration: integrates Curator, ZooKeeper `CreateMode`, Hadoop path exceptions, registry security ACL constants, and `CuratorEventCatcher`.

Risks and test signals: strong coverage of wrapper exception mapping and idempotent delete semantics. It does not deeply assert node data contents after update, only operation success/failure.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HadoopUsersConfTestHelper.java

Purpose: Test helper for user, group, and proxyuser configuration used by MiniDFS and HTTPFS tests.

Important APIs/types/functions: `getHadoopProxyUser`, `getHadoopProxyUserHosts`, `getHadoopProxyUserGroups`, `getHadoopUsers`, `getHadoopUserGroups`, `getBaseConf`, and `addUserConf`.

Control flow: static initialization loads test properties. Getters read system properties with defaults: current user for proxyuser, `*` hosts/groups, and default users `user1`/`user2` with groups `group1`/`supergroup` when no explicit `test.hadoop.user.*` properties exist. `getBaseConf` copies all system properties into a Hadoop `Configuration`. `addUserConf` sets simple authentication/proxyuser keys and creates test UGI users for each configured user.

State and persistence: mutates Hadoop `UserGroupInformation` static test users and reads JVM system properties. No files directly.

Dependencies/integration: Hadoop `Configuration`, UGI, and `SysPropsForTestsLoader`.

Risks and test signals: essential for reproducible HTTPFS proxyuser tests. The identity comparison `getHadoopUsers() == DEFAULT_USERS` works only because the method returns the static array in the default branch; future refactors could break default group detection.

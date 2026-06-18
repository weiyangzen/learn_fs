# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterWithSecureStartup.java

Purpose: covers secure Router startup validation for Kerberos/SPNEGO-related configuration in the Router WebHDFS contract.

Important APIs/types/functions: `SecurityConfUtil.initSecurity`, `RouterWebHDFSContract.createCluster`, `RouterWebHDFSContract.getCluster`, `DFS_ROUTER_KEYTAB_FILE_KEY`, and the HTTP auth principal key `hadoop.http.authentication.kerberos.principal`. The helper `testCluster()` removes a required key and expects cluster creation to fail with `IOException`.

Control flow: `testStartupWithoutSpnegoPrincipal()` unsets the SPNEGO principal and expects startup to still succeed because the HTTP auth principal has a default. `testStartupWithoutKeytab()` removes the router keytab file key and asserts secure mode fails. `testSuccessfulStartup()` uses the full security configuration and expects a cluster object.

State and persistence behavior: no custom persistence is added by this class; cluster lifecycle is delegated to `RouterWebHDFSContract`. Integration points are secure Hadoop configuration, Router startup, keytab validation, and WebHDFS contract utilities. Risks include shared static contract cluster state and brittle assertion messages if startup validation text changes. Test signals are successful cluster creation for valid/defaulted configs and `IOException` for missing keytab.

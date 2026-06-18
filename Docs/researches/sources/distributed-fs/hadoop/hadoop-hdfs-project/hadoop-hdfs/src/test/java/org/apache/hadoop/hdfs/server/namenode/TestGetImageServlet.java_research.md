# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestGetImageServlet.java

**Purpose:** Unit coverage for `ImageServlet.isValidRequestor()`, which authorizes HTTP fsimage/edits transfer requestors in secure HA NameNode deployments.

**Important APIs and flow:** The test creates an `HdfsConfiguration`, installs simple Kerberos short-name rules, configures nameservice `ns1` with HA NameNodes `nn1` and `nn2`, and sets NN RPC addresses and Kerberos principals. `NameNode.initializeGenericKeys(conf, "ns1", "nn1")` makes the configuration look like NN1. A mocked `ServletContext` returns a mocked `AccessControlList` from `HttpServer2.ADMINS_ACL`.

**Control flow:** With ACL initially denying all users, the test asserts `hdfs/host2@TEST-REALM.COM` is still a valid requestor because it corresponds to the peer HA NameNode. It then marks short user `atm` as an admin, verifies the peer NN remains valid, verifies `atm@TEST-REALM.COM` is valid, and verifies unrelated `todd@TEST-REALM.COM` is rejected.

**State and persistence behavior:** There is no filesystem or persistent state. The tested state is configuration-derived Kerberos principal mapping plus servlet-context ACL lookup.

**Dependencies and integration points:** Integrates `ImageServlet`, `DFSUtil.addKeySuffixes()`, HA NameNode config keys, `KerberosName`, `UserGroupInformation`, `AccessControlList`, `HttpServer2.ADMINS_ACL`, and Mockito.

**Risks and test signals:** The test depends on principal host substitution and Kerberos short-name rules matching current implementation. Passing signals fsimage transfer authorization admits HA peer NameNodes independently of admin ACLs, admits configured administrators, and rejects ordinary users.

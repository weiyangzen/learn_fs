# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/RegistryTestHelper.java

Purpose: shared assertions, sample records, endpoint builders, Kerberos login helpers, and logging utilities for registry tests.

Important APIs and functions: constants define canonical test paths and endpoint APIs. `validateEntry()`, `assertMatches()`, and `findEndpoint()` verify service-record structure. `buildExampleServiceEntry()` and `addSampleEndpoints()` create realistic external and internal endpoints. Kerberos helpers include `enableKerberosDebugging()`, `logout()`, and `loginUGI()`.

Control flow: record validation locates endpoints by API, checks address/protocol types, tuple counts, and selected address values. Record comparison checks description, attributes, and endpoint counts, but does not deeply compare every endpoint field. Sample endpoint creation mixes URI, REST, Thrift, hostname/port, and IPC endpoint builders.

State and persistence: no persistent state beyond a static `ServiceRecordMarshal` and constants. Login helpers can change JVM security debug properties and create UGI login state through Hadoop security.

Dependencies and integration: integrates `RegistryTypeUtils`, `RegistryUtils`, YARN registry attributes, JUnit assertions, ZooKeeper path validation, JAAS login context, and Hadoop UGI.

Risks and test signals: helpers are heavily reused, so assertion gaps can propagate. `createRecord(String id, String persistence, String description, String data)` ignores `data`, which is safe for current tests but may surprise future test authors.

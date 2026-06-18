# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationMBean.java

Purpose: JMX contract for federation-wide Router metrics and status.

Important APIs and types: private evolving interface exposing JSON views for namenodes, nameservices, mount table, routers, capacities as `long` and `BigInteger`, datanode counts, block/file counts, Router identity/status/security, corrupt files, low redundancy, scheduled replication, and SPS paths.

Control flow: no implementation; consumers call getters through JMX or metrics code.

State and persistence: interface has no state. Implementations aggregate state from Router, State Store, membership records, and downstream NameNodes.

Dependencies and integration points: implemented by RBF metrics classes and consumed by operators, tests, JMX clients, and compatibility code that expects NameNode-like metrics on the Router.

Risks: method names are a compatibility surface. Deprecated Router identity methods remain for older clients. Large capacities can overflow `long`, hence BigInteger alternatives. Tests should validate implementation JSON shape and capacity aggregation, including overflow-safe methods.

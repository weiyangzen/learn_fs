# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/conf/hadoop-policy.xml

Purpose: default service-level authorization policy file for Hadoop RPC protocols. It defines ACL properties for HDFS, MapReduce, YARN, HA, journal, refresh, router, and timeline-related protocols, with checked-in defaults allowing all users. The source was read as a complete 325-line XML file.

Important APIs/functions: properties include `security.client.protocol.acl`, `security.client.datanode.protocol.acl`, `security.datanode.protocol.acl`, `security.inter.datanode.protocol.acl`, `security.datanode.lifeline.protocol.acl`, `security.namenode.protocol.acl`, `security.admin.operations.protocol.acl`, refresh protocol ACLs, `security.ha.service.protocol.acl`, router and ZKFC ACLs, qjournal ACLs, MapReduce history/client/task ACLs, and many YARN protocol ACLs. All visible values are `*`.

Control flow: no executable control flow. Hadoop authorization code loads this XML by the `hadoop.policy.file` system property or default `HADOOP_POLICYFILE` and checks protocol ACLs when service-level authorization is enabled.

State and persistence: persistent policy state. In this default form it is permissive; production deployments are expected to override values with users and groups.

Dependencies and integration: integrated through the Hadoop `Configuration` loader and service authorization manager. The shell layer defaults `HADOOP_POLICYFILE` to `hadoop-policy.xml`, and admin refresh commands can reload policy at runtime.

Risks: default `*` ACLs are intentionally broad and must be tightened for secured clusters. Property-name drift between protocol implementations and this file can leave a service with unintended defaults. XML syntax errors can break policy loading or refresh.

Test signals: XML validation, service authorization unit tests for each protocol key, `dfsadmin`/`rmadmin` policy refresh tests, secure cluster integration tests with restrictive ACLs, and negative tests verifying unauthorized users are rejected.

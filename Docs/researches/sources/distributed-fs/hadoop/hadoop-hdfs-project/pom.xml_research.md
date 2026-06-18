# sources/distributed-fs/hadoop/hadoop-hdfs-project/pom.xml

Purpose: Maven aggregator POM for the Hadoop HDFS project. It groups HDFS modules under the parent `hadoop-project` build.

Important structure: packaging is `pom`; artifact is `hadoop-hdfs-project` version `3.6.0-SNAPSHOT`; modules include `hadoop-hdfs`, `hadoop-hdfs-client`, `hadoop-hdfs-native-client`, `hadoop-hdfs-httpfs`, `hadoop-hdfs-nfs`, and `hadoop-hdfs-rbf`.

Control flow: Maven traverses declared modules during reactor builds. The build config skips deployment through `maven-deploy-plugin` and configures Apache RAT without additional local options.

State and persistence behavior: no runtime state. Build outputs are produced by child modules under their respective targets.

Dependencies and integration points: inherits dependency/plugin management from `../hadoop-project`. It is the integration root for HDFS server, client, native client, HTTPFS, NFS, and Router-Based Federation modules.

Risks: module ordering and parent-relative path are critical for reactor resolution. Skipping deploy at this aggregator prevents accidental deployment of the aggregate POM but child deploy behavior depends on child configuration.

Test signals: successful Maven reactor loading confirms all listed child module paths exist and the parent POM is resolvable.

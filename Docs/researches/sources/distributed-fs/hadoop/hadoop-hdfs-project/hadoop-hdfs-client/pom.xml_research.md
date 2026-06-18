# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/pom.xml

Purpose: Maven module definition for the Hadoop HDFS client jar.

Important configuration: parent is `hadoop-project-dist`; artifact is `hadoop-hdfs-client`; component property is `hdfs`; packaging is `jar`. Dependencies include provided `hadoop-common`, Apache HTTP client/core, Jakarta JAX-RS API, Jackson annotations/databind, JUnit 5, Mockito inline, Netty test dependencies, MockServer, and Hadoop common test jar.

Control flow and build behavior: Surefire is declared for tests. RAT excludes `dev-support/findbugsExcludeFile.xml`. Protobuf plugin compiles sources with an additional proto path to common protos. Maven replacer runs on generated, main, and test sources. Javadoc excludes generated protocol protobuf packages.

State and persistence: no runtime state; defines build graph, generated sources, and test dependencies.

Dependencies and integration: supports HDFS client classes such as `Hdfs`, WebHDFS wrappers, protocol types, and RPC/protobuf alignment context code.

Risks and test signals: dependency scope choices are important: `hadoop-common` is provided for main code but test jar is test-scoped. Generated proto and replacer execution are essential for protocol classes used by `ClientGSIContext`.

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/pom.xml

Purpose: this Maven POM defines the `hadoop-hdfs-httpfs` module, its compile/test dependencies, resource filtering, test execution settings, static-analysis exclusions, and distribution profile.

Important APIs and types: artifact `org.apache.hadoop:hadoop-hdfs-httpfs:3.6.0-SNAPSHOT` inherits from `hadoop-project`; compile dependencies include Hadoop auth/common/hdfs, Jersey, servlet API, Jetty, json-simple, shaded Guava, reload4j/slf4j, and provided `hadoop-hdfs-client`; test dependencies include Hadoop test jars, Mockito inline, BouncyCastle, Kotlin stdlib, and JUnit 5.

Control flow: resources filter `httpfs.properties` separately from other resources; test resources filter `krb5.conf`. Surefire runs single-threaded with timeout/listener settings and excludes Kerberos tests by default. Antrun copies the webapp into test classes and generates site HTML from `httpfs-default.xml`. Javadoc groups HttpFS API packages. SpotBugs uses the module and global exclusion files. Profiles enable Kerberos tests or assemble the HttpFS distribution.

State and persistence: persistent build metadata includes source repository/revision placeholders, build timestamp, Kerberos realm, exclusion properties, and resource filtering rules. Build outputs include copied webapp test resources, generated site HTML, test classes, and optional distribution archives.

Dependencies and integration points: integrates HttpFS with Hadoop web/auth/security stacks, Jetty/Jersey servlet runtime, HDFS clients, Maven Surefire, RAT, Javadoc, Antrun, SpotBugs, and Hadoop assembly descriptors.

Risks: explicit dependency exclusions avoid servlet/Jetty conflicts but can become stale as parent dependencies evolve. Default Kerberos exclusion means secure-path tests only run under the `testKerberos` profile.

Test signals: enforces JUnit timeout listener, single-thread test execution, Kerberos profile isolation, SpotBugs suppression scope, RAT exclusions, and generated webapp resources needed by HttpFS tests.

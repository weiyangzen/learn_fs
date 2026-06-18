# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/pom.xml

## Purpose
This Maven module descriptor builds the `hadoop-hdfs` server-side jar for Apache Hadoop HDFS 3.6.0-SNAPSHOT. It inherits distribution-wide plugin and dependency management from `hadoop-project-dist`, marks the component as `hdfs`, and binds the module into Hadoop's build, test, webapp, protobuf, RAT, shell-test, and Java-8 compatibility workflows.

## Important build contracts
- Coordinates: parent `org.apache.hadoop:hadoop-project-dist:3.6.0-SNAPSHOT`, artifact `org.apache.hadoop:hadoop-hdfs`, packaging `jar`.
- Main dependencies include `hadoop-auth`, `hadoop-common`, `hadoop-hdfs-client`, Jetty, Jersey, protobuf, Netty, commons libraries, reload4j, shaded Guava, LevelDB JNI, Jackson, and Hadoop annotations.
- Test dependencies add `hadoop-common` test jar, ZooKeeper test jar, MiniKDC, Mockito inline, KMS and KMS test jar, BouncyCastle, Curator test, AssertJ, lz4, and JUnit 5.
- `maven-surefire-plugin` passes `runningWithNative` and installs `TimedOutTestsListener`.
- `maven-antrun-plugin` creates filtered webapp `web.xml` files during `compile`, rebuilds test data/log directories during `process-test-resources`, copies webapps into test classes, and stages `hdfs-default.xml` plus `configuration.xsl` for the site during `pre-site`.
- `protobuf-maven-plugin` compiles HDFS protos while adding Hadoop common and HDFS client proto paths.
- `replacer` runs for generated, main, and test sources, excluding `DFSUtil.java` from main source replacement.
- `hadoop-maven-plugins:resource-gz` gzips static webapp JS/CSS resources.
- `maven-javadoc-plugin` excludes generated protobuf packages from Javadocs.
- RAT excludes generated/binary/test fixtures, bundled web assets, config files, dev-support material, and webapp robots files.
- `maven-clean-plugin` removes site-staged `configuration.xsl` and `hdfs-default.xml`.

## Control flow
The build starts with inherited Hadoop lifecycle defaults, then this POM adds HDFS-specific phases. Compilation generates webapp descriptors and protobuf sources; resource generation gzips web static assets; test-resource processing resets local test state and copies webapps; optional profiles adjust test parallelism, shell testing, or Java 8 source roots. The `shelltest` profile is activated when tests are not skipped and executes `src/test/scripts/run-bats.sh` during the test phase.

## State and persistence behavior
The POM writes only build outputs under `${project.build.directory}` and temporarily copies site resources into `src/site/resources` before clean removes those staged files. Test state is intentionally reset under `${test.build.data}` and `${hadoop.log.dir}`. Parallel tests shard `test.build.data`, `test.build.dir`, and `hadoop.tmp.dir` by `${surefire.forkNumber}` while preserving `test.build.shared.data` for rare inter-fork coordination.

## Dependencies and integration points
This file is the integration hub between HDFS server code, HDFS client APIs, Hadoop common utilities, native/codec stacks, web UI servlets, federation tools, KMS security tests, and shell scripts. Its proto paths couple HDFS server generated classes to common and HDFS-client `.proto` definitions. Its shelltest profile directly validates scripts such as `src/main/bin/hdfs` and `hdfs-config.sh`.

## Risks
- Build behavior depends heavily on parent-managed versions and properties such as `${transient.protobuf2.scope}`, `${leveldbjni.group}`, `${test.build.data}`, and `${release-year}`.
- The antrun phases mutate generated webapp/test/site directories; stale outputs can hide missing source resources if clean is not run.
- RAT excludes are broad and must stay intentional because they can hide license drift in generated or bundled assets.
- Shell tests only run when the profile is active and `skipTests` is not set.
- The `parallel-tests` profile disables fork reuse and rewrites temp paths; tests that assume shared state outside `test.build.shared.data` can fail only in this profile.

## Test signals
- `mvn test -Pshelltest` exercises `src/test/scripts/run-bats.sh`, including focused BATS tests for `hdfs` subcommand dispatch and shell execution naming.
- `mvn test -Pparallel-tests` stresses fork-isolated HDFS tests.
- `TestHdfsConfigFields` compares `DFSConfigKeys` and `HdfsClientConfigKeys` against `hdfs-default.xml`.
- Build failures in protobuf, replacer, RAT, and webapp generation are strong integration signals for this module.

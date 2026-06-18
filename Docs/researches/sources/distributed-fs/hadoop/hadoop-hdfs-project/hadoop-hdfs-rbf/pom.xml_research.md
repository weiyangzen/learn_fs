# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/pom.xml

## Purpose
Maven module descriptor for `hadoop-hdfs-rbf`, the HDFS Router-Based Federation jar. It declares module dependencies, test dependencies, protobuf generation, webapp/resource preparation, static-source replacement, RAT exclusions, cleanup behavior, and a parallel-test profile.

## Important Build APIs and Configuration
The module inherits from `hadoop-project-dist`, sets `hadoop.component=hdfs`, and increases `surefire.fork.timeout` to 3600. Production/provided dependencies include `hadoop-common`, `hadoop-hdfs`, `hadoop-hdfs-client`, `hadoop-federation-balance`, `slf4j-reload4j`, Jetty AJAX utilities, Jettison, Jackson, and HikariCP. Test dependencies include mini-KDC, HDFS/common/federation-balance test jars, DistCp, ZooKeeper test jar, MapReduce components, Curator test, Derby, Mockito inline, AssertJ, and JUnit Jupiter.

## Control Flow
During `compile`, an antrun execution copies `proto-web.xml` to the generated router webapp `WEB-INF/web.xml`, copies other webapp files, and replaces `{release-year-token}` in HTML. During `process-test-resources`, another antrun execution copies generated webapps into test classes. During `pre-site`, it copies `hdfs-rbf-default.xml` and `configuration.xsl` into site resources. The protobuf plugin compiles module protos with additional proto paths to Hadoop common and HDFS client protos. The replacer plugin is enabled for generated, main, and test sources.

## State and Persistence Behavior
The POM drives generated artifacts under `target`, temporary site resources under `src/site/resources`, and test-specific directories. The clean plugin removes the copied `src/site/resources/hdfs-rbf-default.xml` without following symlinks. The parallel-tests profile isolates forked test directories through `${surefire.forkNumber}` and preserves a shared-data directory for rare cross-fork coordination.

## Dependencies, Risks, and Test Signals
This file ties RBF to core HDFS, client protocol protobufs, federation balancing, router web UI assets, protobuf code generation, Hadoop's test infrastructure, and Maven quality plugins. Build changes here have broad blast radius because generated protobuf sources, router web UI packaging, and test classpath are all controlled here. Signals include Maven compile success with generated protos, surefire execution with Derby log isolation, webapp resources present for tests, RAT passing with explicit excludes, and parallel profile creating fork-scoped dirs.

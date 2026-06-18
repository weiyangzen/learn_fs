<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/pom.xml -->
# sources/distributed-fs/alluxio/core/server/master/pom.xml

## Purpose
Defines the Maven module for `alluxio-core-server-master`, the jar containing Alluxio master services, REST documentation generation, and exported test classes.

## Important APIs, Types, And Functions
- Parent artifact is `alluxio-core-server`; artifact id is `alluxio-core-server-master`.
- Internal dependencies include common, transport, client-fs, server-common, job-client, and stress-shell modules.
- External dependencies cover AWS S3 SDK, Guava, Dropwizard metrics, Swagger/Jersey/Jetty REST support, RocksDB JNI, fastutil, and servlet APIs.
- Build plugins create a test jar and generate Swagger REST documentation for `AlluxioMasterRestServiceHandler`.

## Control Flow
Maven inherits common configuration from the parent, resolves module dependencies, packages master classes as a jar, optionally exports test classes, and can generate REST API documentation into `generated/master`.

## State And Persistence Behavior
Build output is Maven target data and generated Swagger/static documentation. The POM itself does not encode runtime state, but dependency choices enable runtime persistence implementations such as RocksDB-backed metastores.

## Dependencies And Integration Points
Integrates the master module with Alluxio's multi-module build, underfs implementations for tests, S3 proxy tests, HTTP client, Jersey REST stack, metrics, and RocksDB. The module is central to runtime and test classpath composition.

## Risks And Edge Cases
Dependency scope matters: Jersey JSON is provided, while underfs S3A is test-scoped. Incorrect scopes could bloat runtime artifacts or break tests. The module also repeats `build.path` so running Maven from subproject directories works.

## Test Signals
The test-jar plugin indicates downstream modules rely on master test utilities. Successful Maven test/package runs validate dependency compatibility and REST doc generation configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/pom.xml -->

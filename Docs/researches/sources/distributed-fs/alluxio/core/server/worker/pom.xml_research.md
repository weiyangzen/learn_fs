# sources/distributed-fs/alluxio/core/server/worker/pom.xml

Purpose: this Maven POM defines the `alluxio-core-server-worker` jar module, its dependencies, and REST API documentation generation for worker endpoints.

Important elements include parent `alluxio-core-server`, artifact ID, `jar` packaging, module description, local `build.path`, external dependencies for Guava, Commons IO/Lang, Dropwizard metrics, servlet, Jetty, Jersey, and Jackson JSON, plus internal dependencies on client FS, common, transport, server-common, and Fuse integration. Test dependencies include Hamcrest, common test jar, local UFS, and HDFS UFS. The build config adds `swagger-maven-plugin` pointing at `alluxio.worker.AlluxioWorkerRestServiceHandler` and generates worker REST docs under `generated/worker`.

State and persistence are build metadata only. Integration points are compilation/runtime classpaths for worker web, REST, storage, metrics, and UFS behavior. Risks include provided-scope JSON dependency assumptions, test-only UFS dependencies needed by reflection, and generated documentation drifting if REST annotations or paths change. Test signal is indirect: this module's tests and Swagger generation depend on the dependencies declared here.

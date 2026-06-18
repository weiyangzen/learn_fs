## sources/distributed-fs/alluxio/core/server/common/pom.xml

### Purpose
This Maven module descriptor defines `alluxio-core-server-common`, the shared server-side utility jar for Alluxio core services.

### Important APIs, Types, And Functions
The artifact inherits from `alluxio-core-server`, packages as `jar`, names the module "Alluxio Core - Server - Common Utilities", defines `build.path`, and pins `alluxio.ratis.version` to `2.4.1`.

### Control Flow
Maven uses this file to resolve dependencies and build/test the module. There is no runtime control flow.

### State And Persistence
Build state is Maven artifact metadata and dependency resolution. No application persistence.

### Dependencies And Integration Points
External dependencies include Kryo, Apache Ratis server/grpc, Atomix Catalyst transport, Jackson, Guava, JAXB runtime, Commons CLI/Lang/Compress, Dropwizard metrics, Prometheus clients, Servlet/JAX-RS APIs, Curator, Jetty, protobuf Jackson datatype, and LZ4. Internal dependencies are `alluxio-core-common`, `alluxio-core-transport`, and the core-common test jar for tests.

### Risks
Server common is a dependency-heavy module; version drift in Ratis, Jackson, Jetty, or metrics libraries can affect masters/workers. The Catalyst dependency is explicitly marked with a TODO for removal. Runtime JAXB is required by AWS SDK paths.

### Test Signals
Maven compilation and module tests validate dependency compatibility. The listed Java utilities depend on these declared internal/external libraries.

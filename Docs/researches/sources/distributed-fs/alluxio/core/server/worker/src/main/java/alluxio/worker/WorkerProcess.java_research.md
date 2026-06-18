# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/WorkerProcess.java

Purpose: `WorkerProcess` defines the public process contract for an Alluxio worker and a factory for constructing the default implementation.

Important APIs include `Factory.create`, `Factory.create(TieredIdentity)`, address getters, UFS manager access, start-time/uptime getters, typed `getWorker`, and inherited `Process` lifecycle methods. Control flow in the factory builds a local tiered identity from global configuration and returns `AlluxioWorkerProcess`.

State and persistence are implementation-defined; the interface exposes worker network identity, data/web ports, optional domain socket path, and registered worker services. Dependencies include Alluxio `Process`, configuration, tiered identity factory, UFS manager, and wire network address. Integration points are `AlluxioWorker`, `WorkerWebServer`, tests, and other server components that need to inspect or control the worker. Risks are mainly contract assumptions: some getters are documented as unit-test-only, and `getWorker` returns null or implementation-specific instances depending on registry contents. No direct tests are in this subset.

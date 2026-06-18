# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/web/WorkerWebServer.java

Purpose: `WorkerWebServer` hosts worker REST endpoints and, when enabled, worker web UI static assets.

Important APIs are the constructor and `stop`. Control flow creates a Jersey `ResourceConfig` scanning `alluxio.worker` and `alluxio.worker.block`, registers protobuf object mapping, creates a file-system client, and installs servlet-context references to the `WorkerProcess` and file-system client. It binds the REST servlet under `Constants.REST_API_PREFIX/*`. If `WEB_UI_ENABLED` is true, it serves `WEB_RESOURCES/worker/build`, sets `index.html` as welcome file, installs a default servlet, and maps 404s to `/` to support client-side routing.

State and persistence include the owned `FileSystem` client and servlet context attributes. Dependencies include Jetty, Jersey, Alluxio configuration, `BlockWorker`, and web utilities. Integration points are `AlluxioWorkerProcess` construction and `AlluxioWorkerRestServiceHandler`, which reads these context attributes. Risks include malformed resource path logging but not failing startup, static UI disabled by config, and REST construction requiring a non-null block worker. No direct tests in this subset cover server startup or UI fallback.

# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RequestServlet.java

`S3RequestServlet` is the servlet-v2 S3 entry point. It handles requests under `S3_V2_SERVICE_PATH_PREFIX`, creates an `S3Handler`, stores it on the request, and invokes the selected `S3BaseTask`.

When async processing is enabled, it selects a light or heavy executor from servlet context based on the task `OpTag`, starts a servlet `AsyncContext`, and completes it after task execution. Synchronous mode calls `serveRequest` directly. Complete multipart upload uses `handleTaskAsync`; other operations call `continueTask()` and `S3Handler.processResponse`.

The servlet holds only static config-derived flags and does not persist data. Integration points are Alluxio configuration, servlet async APIs, `ProxyWebServer` executor attributes, `S3Handler`, and `S3ErrorResponse`. Tests should cover target/non-target paths, handler creation failures, sync/async execution, missing executors, light/heavy routing, async timeout behavior, and complete multipart special handling.

# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3BaseTask.java

`S3BaseTask` is the abstract command base for servlet-v2 S3 handling. It binds an `S3Handler` to an `OpType`, requires subclasses to implement `continueTask()`, and exposes `handleTaskAsync()` as an override hook for operations such as complete multipart upload.

The `OpType` enum names bucket and object S3 APIs and assigns an `OpTag` of `LIGHT` or `HEAVY`, which `S3RequestServlet` uses to select executor pools. The class does not persist state; concrete tasks perform filesystem mutations.

Integration points are `S3ObjectTask.Factory`, `S3BucketTask.Factory`, and `S3RequestServlet.serveRequest`. Tests should verify routing from verb/query/header combinations to expected `OpType`, light/heavy executor classification, and specialized async handling for multipart completion.

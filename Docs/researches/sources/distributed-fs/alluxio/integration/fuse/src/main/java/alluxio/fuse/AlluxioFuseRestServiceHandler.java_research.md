# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioFuseRestServiceHandler.java

Purpose: Jersey REST resource for operational FUSE service control. The current surface is a single log-level mutation endpoint under `/fuse/logLevel`.

Important APIs and flow: `logLevel(@QueryParam logName, @QueryParam level)` wraps `LogUtils.setLogLevel` with `RestUtils.call`, using global configuration for response handling. Constants define the service prefix and query names.

State, dependencies, risks, and tests: it mutates logging state and has no local persistence. It is integrated by `FuseWebServer`, which scans package `alluxio.fuse` under Alluxio's REST API prefix. Risks include exposing runtime log mutation when the FUSE web server is enabled and relying on caller-provided logger names/levels. No direct assigned unit test covers this handler.

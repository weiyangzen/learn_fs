# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/FuseWebServer.java

Purpose: Jetty/Jersey web server wrapper for FUSE REST endpoints.

Important APIs and flow: constructor delegates to `WebServer`, builds a Jersey `ResourceConfig` scanning `alluxio.fuse`, registers protobuf-aware Jackson provider, wraps it in a servlet, and mounts it under `Constants.REST_API_PREFIX/*`.

State, dependencies, risks, and tests: state lives in inherited servlet context. It depends on Alluxio web server infrastructure, Jersey, Jetty, and path utilities. Risks include package-wide resource scanning and enabling operational endpoints based on configuration. No direct assigned test covers it.

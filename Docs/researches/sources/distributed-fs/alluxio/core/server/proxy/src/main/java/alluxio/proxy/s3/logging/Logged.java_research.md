# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/logging/Logged.java

Purpose: `Logged` is a Jersey name-binding annotation used to attach request logging behavior to S3 proxy resources or methods.

Important API/type: the annotation is marked with `@NameBinding`, retained at runtime, and targets both types and methods. It has no members. Control flow is declarative: Jersey uses the annotation to bind `RequestLoggingFilter`, which is itself annotated with `@Logged`, to matching resources.

State and persistence are absent. Dependencies are JAX-RS name-binding and Java annotation metadata. Integration occurs through `ProxyWebServer`, which registers package scanning for `alluxio.proxy.s3.logging`, allowing Jersey to discover the filter. Risks are low, but because `RequestLoggingFilter` also has `@PreMatching`, behavior depends on Jersey provider binding semantics; annotating too broadly can increase log volume and expose authorization data. No direct tests in this subset assert binding behavior.

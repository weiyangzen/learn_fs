# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/ServiceUtils.java

## Purpose
`ServiceUtils` centralizes discovery of enabled master service factories.

## Important APIs, Types, And Functions
`getMasterServiceLoader` returns a synchronized `ServiceLoader<MasterFactory>` using the `MasterFactory` class loader. `getMasterServiceNames` iterates factories and returns names for enabled services.

## Control Flow, State, Dependencies, Risks, And Tests
The utility is read-only but drives journal formatting and master startup composition. Dependencies include Java `ServiceLoader` and `MasterFactory`. Risks include raw type warnings, repeated service loading costs, disabled factory filtering differences between formatting and startup, and name stability across releases. Tests should use test service providers to verify loading, filtering, ordering assumptions, and failure behavior for misconfigured factories.

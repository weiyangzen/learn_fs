# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/RegistryTest.java

## Purpose
`RegistryTest` verifies generic server registry dependency ordering, cycle detection, and timeout behavior when a requested server is unavailable.

## Important APIs, Types, and Functions
It defines `TestServer`, `ServerA`, `ServerB`, `ServerC`, and `ServerD`, and tests `registry()`, `cycle()`, and `unavailable()`. It exercises `Registry.add()`, `Registry.getServers()`, and `Registry.get(Class, timeout)`.

## Control Flow, State, and Persistence
`registry()` builds every permutation of A/B/C registration order and asserts the dependency-sorted order is C, B, A. `cycle()` registers servers with a dependency cycle and expects runtime failure. `unavailable()` waits briefly for a missing server and checks the timeout message includes the server class. There is no persistence.

## Dependencies and Integration Points
It depends on the common `Registry`, `Server`, gRPC service types, and JUnit. The same registry pattern underlies master and worker service startup.

## Risks and Test Signals
Risks covered include startup order depending on registration order, undetected dependency cycles, and poor diagnostics for missing services. Passing tests signal deterministic dependency resolution and timeout reporting.

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/AddingCompositeService.java

## Purpose
`AddingCompositeService` is a thin public subclass of Hadoop `CompositeService` that exposes add/remove service methods.

## Important APIs and types
The constructor accepts a service name. `addService(Service)` and `removeService(Service)` simply delegate to the superclass.

## Control flow
There is no additional behavior beyond standard `CompositeService` lifecycle management. The class exists to make child-service composition available to external classes.

## State and persistence behavior
State is inherited child-service lists and lifecycle state. It does not persist registry data.

## Dependencies and integration points
It depends on Hadoop service APIs and is useful for server/test components that need dynamic service composition.

## Risks and test signals
The class documentation warns that adding uninitialized services to an already initialized parent can break lifecycle transitions. Tests should cover add/remove visibility and lifecycle propagation in the intended usage contexts.

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableFactory.java

## Purpose

`WritableFactory.java` defines the factory interface used by `WritableFactories` to construct writable instances.

## Important APIs, types, and functions

- `newInstance()` returns a new `Writable`.
- Javadoc links the interface to `WritableFactories`.

## Control flow

The interface has no implementation control flow. Callers invoke it when a factory has been registered for a writable class.

## State and persistence behavior

State depends on implementations. Factories may be stateless singletons or capture construction context, but the interface does not prescribe persistence.

## Dependencies and integration points

It depends only on `Writable` and Hadoop annotations. It integrates with `WritableFactories` and deserialization code needing factory-based construction.

## Risks and edge cases

- The interface does not accept a `Configuration`; configuration is applied after construction only if the result implements `Configurable`.
- It does not declare checked exceptions, so construction failures must be unchecked.
- Implementations must return a fresh instance unless documented otherwise.

## Test signals

Tests should focus on implementations: fresh-instance behavior, compatibility with `WritableFactories.newInstance()`, configuration injection after construction, and failure propagation.

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableFactories.java

## Purpose

`WritableFactories.java` is a global registry that lets Hadoop construct `Writable` instances through explicit factories rather than public constructors. It is mainly for non-public writable classes or classes needing custom instantiation.

## Important APIs, types, and functions

- `CLASS_TO_FACTORY` is a `ConcurrentHashMap<Class, WritableFactory>`.
- `setFactory(Class, WritableFactory)` registers a factory.
- `getFactory(Class)` returns a registered factory or null.
- `newInstance(Class<? extends Writable>, Configuration)` uses a factory when present, sets configuration on `Configurable` results, or falls back to `ReflectionUtils.newInstance()`.
- `newInstance(Class<? extends Writable>)` delegates with null configuration.

## Control flow

Instantiation first looks up the class in the registry. If a factory exists, it creates the object and applies configuration if the result implements `Configurable`. Without a factory, `ReflectionUtils.newInstance()` performs reflective construction and configuration.

## State and persistence behavior

The only state is the static concurrent factory registry. It persists for the JVM lifetime and is not serialized. Registrations can be replaced by later calls.

## Dependencies and integration points

The class depends on `WritableFactory`, `Writable`, `Configurable`, `Configuration`, `ReflectionUtils`, and `ConcurrentHashMap`. It integrates with object deserialization paths such as `ObjectWritable` and any code that needs configurable writable instantiation.

## Risks and edge cases

- Global mutable registration can affect unrelated code in the same JVM.
- Raw `Class` keys and values provide limited compile-time type safety.
- A factory returning the wrong writable type is not checked locally.
- `setFactory(c, null)` effectively stores a null value attempt, which `ConcurrentHashMap` rejects with `NullPointerException`; removal is not supported.

## Test signals

Tests should verify factory use, fallback reflection, `Configurable.setConf()` application for factory-created objects, replacement registrations, non-public constructors, and wrong/null factory behavior.

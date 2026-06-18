# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configured.java`

## Purpose

`Configured` is a small public stable base class for objects that implement Hadoop's `Configurable` contract. It stores a `Configuration` reference and gives subclasses a conventional implementation of `setConf` and `getConf`.

## Important APIs and Types

The class exposes a no-arg constructor that delegates to `Configured(null)`, a constructor accepting a `Configuration`, `setConf(Configuration)`, and `getConf()`. The stored `conf` field is private and not copied.

## Control Flow

Construction immediately calls `setConf`, allowing subclasses that override `setConf` to participate in initialization. After construction, callers can replace the held configuration at any time through `setConf`.

## State and Persistence

The only state is the `Configuration` reference. There is no synchronization, validation, serialization, cloning, or persistence.

## Dependencies and Integration Points

It depends on the `Configurable` interface and `Configuration`. Many Hadoop tools, services, and helper classes extend this class so they can be initialized by reflection utilities or service frameworks that detect `Configurable`.

## Risks

The no-arg constructor leaves `conf` null, so subclasses must handle null or install defaults. Because the reference is mutable and not synchronized, it is unsuitable as a thread-safe configuration holder without external discipline.

## Test Signals

Tests should verify constructor assignment, replacement through `setConf`, null handling, and subclass override behavior during construction if subclasses depend on that hook.

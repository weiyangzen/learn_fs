# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Reconfigurable.java`

## Purpose

`Reconfigurable` defines the interface for Hadoop components whose `Configuration` can be changed at runtime. It extends `Configurable` with methods for applying one property change and discovering which properties are allowed to change.

## Important APIs and Types

The core methods are `reconfigureProperty(String property, String newVal)`, `isPropertyReconfigurable(String property)`, and `getReconfigurableProperties()`. `newVal == null` means reset the property to its default value.

## Control Flow

Implementations are expected to validate whether a property is reconfigurable, apply the new value to internal state, then update the backing `Configuration`. If the property is not allowed or the value cannot be applied, implementations throw `ReconfigurationException`.

## State and Persistence

The interface owns no state. Implementing classes decide whether changes are only in-memory or are also reflected in external files or service-specific persistent state. The common base implementation updates only the in-memory `Configuration`.

## Dependencies and Integration Points

This is used by `ReconfigurableBase`, `ReconfigurationServlet`, and management tooling. Service daemons expose an instance through servlet context attributes so administrators can compare current and reloaded configuration and apply allowed changes.

## Risks

Correctness depends entirely on implementers keeping `isPropertyReconfigurable`, `getReconfigurableProperties`, and `reconfigureProperty` consistent. A property can be marked reconfigurable but still fail if the implementation cannot safely update all derived runtime state.

## Test Signals

Tests should exercise both allowed and disallowed properties, null default reset semantics, propagation to the backing `Configuration`, and failure paths that preserve old runtime state.

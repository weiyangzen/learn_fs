# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationUtil.java`

## Purpose

`ReconfigurationUtil` compares two `Configuration` instances and returns the changed properties needed by runtime reconfiguration workflows.

## Important APIs and Types

The nested `PropertyChange` type holds public `prop`, `oldVal`, and `newVal` fields. `getChangedProperties(Configuration newConf, Configuration oldConf)` is the static comparator, and `parseChangedProperties` is an instance wrapper used for test injection by `ReconfigurableBase`.

## Control Flow

The comparator first iterates old configuration entries, checking each old value against `newConf.getRaw(prop)` and adding a change when the new raw value is missing or different. It then iterates new configuration entries and adds changes for properties where `oldConf.get(prop)` is null, representing newly introduced settings. A map keyed by property name deduplicates changes from both passes.

## State and Persistence

The utility itself is stateless. `PropertyChange` is mutable and has identity equality because it does not override `equals` or `hashCode`.

## Dependencies and Integration Points

It depends on `Configuration` iteration and raw/value getters. It is used by `ReconfigurableBase` and `ReconfigurationServlet` to compute differences between current in-memory config and freshly loaded defaults/resources.

## Risks

The first pass compares old resolved values with new raw values, while the second pass uses `oldConf.get(prop)`; variable substitution and deprecation side effects can therefore affect comparisons. Because `PropertyChange` is mutable and identity-based, it is best suited for reporting, not set algebra. Changes to final/non-reconfigurable properties are included here and filtered later.

## Test Signals

Tests should cover changed, added, removed, unchanged, null/default, substituted-value, and deprecated-key scenarios, plus duplicate avoidance when a property appears in both passes.

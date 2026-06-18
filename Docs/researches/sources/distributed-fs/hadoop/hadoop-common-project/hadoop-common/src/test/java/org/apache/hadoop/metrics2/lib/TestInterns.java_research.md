# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestInterns.java

## Purpose

`TestInterns` validates interning and bounded cache eviction for metrics metadata (`MetricsInfo`) and tags (`MetricsTag`).

## Important APIs, Types, And Functions

The tests use `Interns.info()`, `Interns.tag()`, cache-size constants `MAX_INFO_NAMES`, `MAX_INFO_DESCS`, `MAX_TAG_NAMES`, and `MAX_TAG_VALUES`, plus `assertSame`/`assertNotSame`.

## Control Flow

Basic tests assert identical name/description or tag triples return the same object. Overflow tests create more distinct names or values than the configured maximum and assert an early object remains interned until the limit is crossed, then is no longer the same object.

## State And Persistence Behavior

The relevant state is global/static intern caches inside `Interns`. No disk state exists. Because caches are global, test order and prior cache population can influence exact eviction behavior if not isolated.

## Dependencies And Integration Points

It integrates with metrics2 metadata construction used throughout collectors, registries, and sinks. Interning reduces object churn and supports fast identity/equality paths.

## Risks And Test Signals

Risks include unbounded cache growth, premature eviction, or failure to preserve object identity for repeated metadata. Signals are object identity assertions before and after cache overflow thresholds.

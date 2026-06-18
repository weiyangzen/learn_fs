# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Lists.java

## Purpose

`Lists` is a Hadoop-local collection utility class modeled after common Guava list helpers, creating mutable list implementations with convenient overloads.

## Important APIs, Types, And Functions

It provides `newArrayList()` overloads for empty lists, varargs elements, iterable/iterator contents, and expected sizes, plus `newLinkedList()` and capacity helper logic for array-list sizing.

## Control Flow, State, And Persistence

All methods are static and allocate new Java list instances. Iterable and iterator overloads copy elements into the new collection. There is no class state or persistence.

## Dependencies And Integration Points

It depends on Java `ArrayList`, `LinkedList`, `Iterator`, `Iterable`, and collection sizing utilities. Hadoop code uses it to avoid direct dependency on relocated or changing Guava APIs.

## Risks And Test Signals

Expected-size calculations must avoid integer overflow and excessive allocation. Tests should cover varargs null elements, iterator exhaustion, iterable copying, expected-size boundaries, and mutability of returned lists.

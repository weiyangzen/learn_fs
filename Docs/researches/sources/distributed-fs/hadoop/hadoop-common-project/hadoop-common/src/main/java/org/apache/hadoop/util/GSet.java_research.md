# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GSet.java

## Purpose

`GSet` defines a set-like collection that also supports key-based retrieval of the stored element. It fills the gap between `Set` and `Map` for objects that act as their own keys.

## Important APIs, Types, And Functions

The interface extends `Iterable<E>` and declares `size()`, `contains(K)`, `get(K)`, `put(E)`, `remove(K)`, `clear()`, and `values()`. The type parameters require stored elements `E` to be assignable to keys `K`.

## Control Flow, State, And Persistence

There is no implementation state here. Implementations decide thread-safety, hashing strategy, replacement semantics, and value-view behavior. The contract rejects null keys/elements.

## Dependencies And Integration Points

It depends on Java collections and SLF4J for a shared logger. Implementations in this set include `GSetByHashMap`, `LightWeightGSet`, and `LightWeightResizableGSet`, used by memory-sensitive Hadoop structures.

## Risks And Test Signals

The replacement semantics differ from `Set.add()`, so callers must expect `put()` to replace equal elements. Tests for implementations should verify null rejection, value-view backing behavior, iterator behavior, and equality/hash-code consistency.

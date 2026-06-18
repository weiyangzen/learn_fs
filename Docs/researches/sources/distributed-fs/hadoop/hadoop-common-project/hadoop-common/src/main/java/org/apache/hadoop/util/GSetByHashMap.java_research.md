# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GSetByHashMap.java

## Purpose

`GSetByHashMap` is the straightforward `HashMap`-backed implementation of `GSet`, intended when standard Java collection overhead is acceptable.

## Important APIs, Types, And Functions

The constructor accepts initial capacity and load factor. `put(E)` stores the element as both key and value, replacing any equal element. `contains()`, `get()`, `remove()`, `iterator()`, `clear()`, and `values()` delegate to the backing map.

## Control Flow, State, And Persistence

The only state is a private `HashMap<K,E>`. There is no synchronization and no persistence. The values collection and iterator are live views from `HashMap`.

## Dependencies And Integration Points

It depends on `GSet`, `HashMap`, and Java collection iterators. It can be substituted for low-memory `GSet` implementations in tests or less constrained code.

## Risks And Test Signals

`put(null)` throws `UnsupportedOperationException`, while some other methods rely on `HashMap` null behavior despite the `GSet` contract. Tests should cover replacement, returned previous values, live `values()` view, iterator removal semantics inherited from `HashMap`, and null behavior.

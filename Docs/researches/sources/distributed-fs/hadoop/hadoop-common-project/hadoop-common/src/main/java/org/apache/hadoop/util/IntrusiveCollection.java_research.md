# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IntrusiveCollection.java

## Purpose

`IntrusiveCollection` implements a memory-efficient doubly linked collection where elements store their own previous/next pointers for each list they join.

## Important APIs, Types, And Functions

Elements implement `IntrusiveCollection.Element` with `insertInternal()`, `setPrev()`, `setNext()`, `removeInternal()`, `getPrev()`, `getNext()`, and `isInList()`. Collection APIs include `add()`, `addFirst()`, `remove()`, `iterator()`, `contains()`, `retainAll()`, `removeAll()`, and `clear()`. A sentinel root element tracks first and last.

## Control Flow, State, And Persistence

Adding checks null and membership, links around root or tail, calls element insertion, and increments size. Removal unlinks neighboring elements, calls `removeInternal()`, and decrements size. Iterators allow their own `remove()` but do not protect against arbitrary concurrent modification. State is in-memory links owned by elements and the collection size.

## Dependencies And Integration Points

It depends on Java collection interfaces, Hadoop `Preconditions`, and SLF4J. It integrates with high-cardinality metadata structures that need lower per-entry allocation than `LinkedList`.

## Risks And Test Signals

Elements must correctly maintain per-list link fields; a bad implementation can corrupt multiple lists. Tests should cover add-first/add-last order, duplicate add rejection, iterator remove, retain/remove all, clear, multi-list elements, and concurrent-modification caveats.

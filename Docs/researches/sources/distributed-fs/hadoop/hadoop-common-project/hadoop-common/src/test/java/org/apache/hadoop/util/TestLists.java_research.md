# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLists.java

Purpose: simple coverage for Hadoop `Lists` collection factory helpers and partitioning.

Important APIs and types: `Lists.newArrayList()`, `newLinkedList()`, varargs/iterable overloads, `newArrayListWithCapacity`, and `Lists.partition(List,int)`.

Control flow: tests create empty array and linked lists, add records, verify insertion order, build array/linked lists from varargs and `HashSet` iterables, partition a five-item list by sizes 2, 1, and 6, and verify partition counts and tail sizes. Capacity helper tests ensure a list with requested capacity behaves as a normal list after adding three entries.

State and persistence: all state is temporary Java collection contents.

Dependencies and integration points: wraps Java `ArrayList`, `LinkedList`, `HashSet`, and AssertJ/JUnit assertions. The partition helper mirrors Guava-style list partition behavior used by callers that batch work.

Risks: partition off-by-one errors, unexpected empty partitions, unsupported mutation behavior, or incorrect factory overload selection. Test signals are list sizes, element positions, and partition dimensions.

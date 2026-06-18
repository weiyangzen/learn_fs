# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestAvailableSpaceResolver.java

## Purpose
This test validates `AvailableSpaceResolver`, which orders multiple destinations by available nameservice space with a configurable balancer preference.

## Important APIs, Types, and Functions
It uses `AvailableSpaceResolver`, `SubclusterAvailableSpace`, `SubclusterSpaceComparator`, `MultipleDestinationMountTableResolver`, `DestinationOrder.SPACE`, mocked `Router`, `StateStoreService`, `MembershipStore`, `GetNamenodeRegistrationsResponse`, `MembershipState`, and `MembershipStatsPBImpl`. Config keys are `BALANCER_PREFERENCE_KEY` and `BALANCER_PREFERENCE_DEFAULT`.

## Control Flow
`mockAvailableSpaceResolver()` builds mocked membership data for ten subclusters with available space 0 through 9, installs an available-space resolver into a multiple-destination mount table, and creates a `/space` mount with `SPACE` order. Tests with preference `1.0` expect subcluster9 for root and subdir paths. Default preference tests retry until a non-max subcluster appears, proving randomness/probabilistic balancing. Comparator tests sort synthetic subclusters for preference 0, 1, 0.5, default, and invalid values, checking ascending/descending/partial ordering and exception messages. `testChooseFirstNamespace()` asserts the default location is the first ordered namespace.

## State and Persistence
All state is mocked or in-memory. No real state-store driver is used.

## Dependencies and Integration Points
The test integrates destination ordering with membership stats fetched from the membership store. It protects routing behavior for space-balanced multi-destination mounts.

## Risks and Test Signals
The default-preference test is probabilistic and could theoretically retry only max selections, though the retry count reduces that risk. Comparator partial-order assertions are intentionally loose for randomized preferences. Passing tests signal correct highest-space preference, valid range enforcement, and resolver integration with `PathLocation` default destination selection.

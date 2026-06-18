# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestLocalResolver.java

## Purpose
This test validates `LocalResolver`, which prioritizes the subcluster whose NameNode address matches the client locality.

## Important APIs, Types, and Functions
It uses mocked `Router`, `StateStoreService`, and `MembershipStore`, `GetNamenodeRegistrationsResponse`, `MembershipState.newInstance()`, `FederationNamenodeServiceState.ACTIVE`, `LocalResolver.getClientAddr()`, `MultipleDestinationMountTableResolver`, and `DestinationOrder.LOCAL`.

## Control Flow
The test creates three active membership records mapping client0/client1/client2 addresses to subcluster0/subcluster1/subcluster2. It spies `LocalResolver` so `getClientAddr()` returns a mutable `StringBuilder` value. A `/local` multi-destination mount is added with LOCAL ordering. Resolution defaults to subcluster0 for unknown clientX, then returns subcluster2, subcluster1, and subcluster0 as the mocked client changes.

## State and Persistence
State is mocked membership data, the mutable client string, and the in-memory mount table. There is no real router state store.

## Dependencies and Integration Points
The test integrates `LocalResolver` with membership-store lookup and the multiple-destination resolver. It protects client-local routing decisions for multi-subcluster mount entries.

## Risks and Test Signals
The test relies on Mockito spying to override network client address discovery. It only tests active memberships and exact host string matching before ports. Passing tests signal that known clients route to their local subcluster and unknown clients fall back to the original/default destination order.

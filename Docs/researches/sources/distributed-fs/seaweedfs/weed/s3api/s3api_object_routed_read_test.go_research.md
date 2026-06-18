# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_read_test.go

## Purpose

This test file pins the unreachable-owner cache used by routed reads.

## Important APIs, Types, and Functions

`TestOwnerRecentlyUnreachable` calls `ownerRecentlyUnreachable` and `markOwnerUnreachable` with `pb.ServerAddress` keys.

## Control Flow

It verifies an unmarked owner is not flagged, a marked owner is flagged within the TTL, and a different owner is unaffected.

## State and Persistence Behavior

Only in-memory server state is mutated; no filer or disk state is used.

## Dependencies and Integration Points

The test depends on routed-read helper methods and protects `getObjectEntryRoutedByKey` failover behavior.

## Risks and Edge Cases

TTL expiry and concurrent map behavior are not covered.

## Test Signals

The test is a focused signal for owner marking correctness.

# sources/distributed-fs/seaweedfs/weed/filer/redis3/ItemList.go

## Purpose

`redis3/ItemList.go` implements a Redis-backed batched name list over SeaweedFS skiplist primitives for very large directory-child indexes. It was read as a complete 506-line file.

## Important APIs, Types, and Functions

`ItemList` owns a `skiplist.SkipList`, batch size, Redis client, and key prefix. Core methods are `WriteName`, `DeleteName`, `ListNames`, `RemoteAllListElement`, `ItemAdd`, and many node helpers such as `NodeAddMember`, `NodeRangeBeforeExclusive`, `NodeDeleteAfterExclusive`, and `NodeScanInclusiveAfter`.

## Control Flow

`WriteName` finds the greater-or-equal skiplist node, avoids duplicates, prefers adding to the previous node if there is capacity, splits a full node around the new name, can merge into the next node for reverse-order inserts, or creates a new node. `DeleteName` removes leading-key or in-batch names, deletes empty nodes, and merges adjacent batches when combined size is below the batch limit. `ListNames` starts at the relevant node and scans nodes in order.

## State and Persistence Behavior

The skiplist structure and each node's Redis sorted set persist separately. Node member keys are `prefix + elementPointer + "m"`, while skiplist elements are saved by `SkipListElementStore`. Mutations set skiplist change flags used by serialization.

## Dependencies and Integration Points

Depends on `github.com/seaweedfs/seaweedfs/weed/util/skiplist` and Redis sorted-set lex/count operations. It is used by Redis3 directory-child helpers.

## Risks and Edge Cases

The split/merge logic is complex and uses many independent Redis commands, so interrupted updates can leave skiplist metadata and node member sets inconsistent. `DeleteName` assumes `nextNode.Reference()` can be used when merging, which requires careful nil handling.

## Test Signals

Only a Redis benchmark is listed in this subset. Strong tests should cover ascending/reverse inserts, duplicates, node split boundaries, delete-leading-key, delete-middle, merge, empty-list cleanup, and start-from listing.

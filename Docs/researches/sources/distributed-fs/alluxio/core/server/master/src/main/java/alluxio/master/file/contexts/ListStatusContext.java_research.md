# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ListStatusContext.java

Purpose: wraps `ListStatusPOptions` and partial-listing options while tracking progress through a list-status call. It supports full listings, partial pagination, explicit metadata-sync disabling for tests, and per-call listing counters.

Important APIs and types: `create` and `mergeFrom` are overloaded for `ListStatusPOptions.Builder` and `ListStatusPartialPOptions.Builder`. `getPartialOptions`, `listedItem`, `isDoneListing`, `isPartialListing`, `donePartialListing`, `isTruncated`, `setTotalListings`, and `getTotalListings` expose pagination state. `disableMetadataSync` is visible for testing.

Control flow: partial-listing construction wraps the embedded full `options` from the partial builder while retaining the partial builder separately. Each listed candidate calls `listedItem`, which increments processed count, skips until `offsetCount`, increments listed count for emitted items, and marks truncation/done when listed count exceeds `batchSize`.

State and persistence behavior: no persistence, but its counters and flags determine response shape and whether traversal can stop early. `disableMetadataSync` mutates the underlying options to `LoadMetadataPType.NEVER` and sync interval `-1`.

Dependencies and integration points: depends on list status protobufs, `FileSystemMasterCommonPOptions`, `LoadMetadataPType`, configuration defaults, and `OperationContext`. It integrates with master listing traversal, partial listing RPCs, and metadata-sync policy checks.

Risks: the batch-size check uses `< mListedCount`, so the item that crosses the limit is not listed and truncation is set after incrementing. Misunderstanding offset versus listed counters can cause off-by-one pagination bugs. `disableMetadataSync` is test-visible and mutates options in a way that production code should avoid unless intentional.

Test signals: strong tests should cover offset-only, batch-only, offset-plus-batch, start-after partial listings, recursive total listing count, truncation flags, and disabled metadata sync option mutation.

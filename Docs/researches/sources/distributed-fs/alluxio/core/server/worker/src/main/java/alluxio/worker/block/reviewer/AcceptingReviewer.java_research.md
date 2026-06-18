# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/AcceptingReviewer.java

Purpose: Reviewer implementation that disables review rejection by accepting every proposed allocation.

Important APIs: `acceptAllocation` always returns true.

Control flow: Allocators call this after finding candidate dirs when review is not skipped.

State and persistence: Stateless.

Dependencies and integration: Implements `Reviewer`; can be selected via `WORKER_REVIEWER_CLASS`.

Risks and test signals: No behavior risk besides disabling buffer protection. Tests should verify it accepts dirs regardless of capacity state supplied by the allocator.

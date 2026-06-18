# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Listing.java

Purpose: S3A listing helper that turns S3 object-list responses into Hadoop `RemoteIterator` streams of `S3AFileStatus` and `S3ALocatedFileStatus`, with filtering, pagination, asynchronous prefetch of next list batches, audit-span retention, and IO statistics aggregation.

Important APIs/types: class extends `AbstractStoreOperation`. Public/package methods create provided status iterators, file-status listing iterators, located-status iterators, single-status iterators, recursive/non-recursive directory listings, non-empty-directory listings, and list-object requests. Nested types include `FileStatusAcceptor`, `FileStatusListingIterator`, `ObjectListingIterator`, `AcceptFilesOnly`, `AcceptAllButS3nDirs`, `AcceptAllObjects`, `AcceptAllButSelfAndS3nDirs`, and `AcceptAllButSelf`.

Control flow: high-level listing methods build an S3 request using key prefixes and delimiters, then construct `ObjectListingIterator`. That iterator launches the initial async list call at construction. Its first `next()` awaits the initial future and, if truncated, schedules the next async batch. Later `next()` calls await the previously scheduled continuation and schedule another when needed. `FileStatusListingIterator` consumes each `S3ListResult`, filters S3 objects and common prefixes through a path filter and acceptor, converts objects to `S3AFileStatus`, and loops through empty filtered batches until data or remote exhaustion.

State and persistence behavior: iterators keep transient pagination state: current request, latest and previous results, future for the in-flight batch, first-listing flag, listing count, batch iterators, IO statistics, and retained audit span. `close()` aggregates iterator IO statistics into the current IO statistics context. No filesystem state is mutated by listing.

Dependencies and integration points: depends on AWS SDK S3 object/prefix models, S3A request/list result wrappers, `ListingOperationCallbacks`, `StoreContext`, audit spans, `S3AUtils` conversion helpers, role-model key conversion, Hadoop `RemoteIterator`, path filters, located statuses, and IO statistics.

Risks: `hasNext()` can trigger remote work indirectly through `FileStatusListingIterator` because filtering may need more batches before it can answer. Iterators are explicitly not thread-safe. Correct acceptor selection is important to suppress self entries, old S3N `_$folder$` markers, and directory marker objects. The async prefetch path must preserve audit context and handle future failures through `onceInTheFuture`.

Test signals: tests should cover provided-status filtering, recursive delimiter behavior, self and S3N marker suppression, file-only acceptor behavior, common-prefix directory status creation, pagination continuation, empty filtered pages, IO statistics aggregation on close, and async future exception translation.

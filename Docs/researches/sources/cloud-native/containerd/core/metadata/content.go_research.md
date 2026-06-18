# sources/cloud-native/containerd/core/metadata/content.go

## Purpose

This file implements a metadata-backed, namespace-aware content store wrapper. It controls content visibility, label metadata, ingest tracking, shared vs isolated namespace policy, lease attachment, event publication, and backend content cleanup.

## Important APIs, Types, and Functions

`newContentStore` constructs `contentStore`, which embeds a backend `content.Store`. Public methods include `Info`, `Update`, `Walk`, `Delete`, `ListStatuses`, `Status`, `Abort`, `Writer`, and `ReaderAt`. `namespacedWriter` wraps backend writers and implements `Close`, `Write`, `Digest`, `Truncate`, `Commit`, `Sync`, `Status`, plus internal `createAndCopy` and `commit`. Helpers include `getRef`, `isSharedContent`, `validateInfo`, `readInfo`, `writeInfo`, `readExpireAt`, `writeExpireAt`, and `garbageCollect`.

## Control Flow

Reads require a namespace and verify the digest exists in namespace metadata before accessing backend content. `Writer` validates a non-empty ref, checks for existing namespace content, optionally marks an existing backend blob as shared, creates an ingest bucket and lease reference, writes a backend ref unless shared, and returns a namespaced writer. `namespacedWriter.Commit` syncs backend writes before opening the metadata transaction, validates size/digest, commits backend content if needed, creates the namespace blob bucket, writes timestamps/labels/size, removes ingest metadata and lease, attaches content to the current lease, and publishes a create event outside transactions. `Delete` removes namespace blob metadata, removes lease references, marks DB/content dirty, and publishes a delete event.

## State and Persistence Behavior

Content metadata is stored under `v1/<namespace>/content/blob/<digest>` with timestamps, size, and labels. Active ingests live under `v1/<namespace>/content/ingests/<ref>` with backend ref, optional expiration, and optional expected digest. Backend content is shared physically, while namespace metadata controls access. GC later deletes unreferenced backend blobs and aborts unreferenced backend ingests. Lease context can attach content or ingests under namespace lease buckets.

## Dependencies and Integration Points

The wrapper integrates `core/content`, metadata DB transactions, leases, namespace context, local/shared namespace labels, events, errdefs, OCI descriptors, OpenContainers digests, bbolt, label validation, and metadata GC. It is returned by `DB.ContentStore()`.

## Risks and Edge Cases

Writer shared mode can return a nil backend writer until data is written or truncated; methods must handle that split path. Commit tolerates backend AlreadyExists but still needs metadata creation to avoid duplicate namespace records. Sync before metadata lock reduces long lock holds but assumes writer implements `content.Syncer`. `ListStatuses` and `Status` translate namespace refs to backend refs, so stale ingest metadata can hide backend status. `isSharedContent` scans all namespaces for the shared label and matching blob, which can be expensive.

## Test Signals

`content_test.go` runs containerd content suites for shared and isolated policies plus lease tests for committed content and active ingests. Additional tests should cover event publication, stale ingest expiration, shared writer copy-on-write through `Write`/`Truncate`, label field updates, backend cleanup, and access denial across namespaces.

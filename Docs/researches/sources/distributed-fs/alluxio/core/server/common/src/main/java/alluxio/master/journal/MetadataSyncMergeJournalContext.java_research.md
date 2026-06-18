# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/MetadataSyncMergeJournalContext.java

## Purpose
`MetadataSyncMergeJournalContext` adapts filesystem merge journaling for metadata sync by avoiding synchronous flushes on normal flush/close.

## Important APIs, Types, And Functions
It extends `FileSystemMergeJournalContext`. `flush` and `close` only append merged entries to the underlying context and do not close or synchronously flush it. `hardFlush` appends and then flushes the underlying context. `getMerger` exposes the merger for tests.

## Control Flow, State, Dependencies, Risks, And Tests
Metadata sync worker threads use separate instances while an RPC thread owns the underlying context. Persistence is delayed until the underlying context is eventually flushed/closed or `hardFlush` is called. Dependencies are merge context base class and `JournalEntryMerger`. Risks include data loss if caller assumes close is durable, under-documented ownership of underlying context, and delayed standby visibility. Tests should cover async flush semantics, hardFlush durability, no underlying close on close, merger exposure, and metadata-sync multi-thread expectations.

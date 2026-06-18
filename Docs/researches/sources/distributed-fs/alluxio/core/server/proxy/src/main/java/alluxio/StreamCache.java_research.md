# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/StreamCache.java

## Purpose
`StreamCache` stores open Alluxio `FileInStream` and `FileOutStream` objects for the REST proxy. Path endpoints return integer stream IDs, and stream endpoints use those IDs to read, write, or close the cached streams.

## Important APIs, Types, and Functions
The class exposes `getInStream`, `getOutStream`, overloaded `put(FileInStream)`, `put(FileOutStream)`, `invalidate`, and `size`. It uses an `AtomicInteger` ID counter and two Guava `Cache<Integer, ...>` instances. A static `RemovalListener<Integer, Closeable>` closes streams when entries expire or are invalidated.

## Control Flow, State, and Persistence
Construction creates input and output caches with `expireAfterAccess(timeoutMs)`. Each `put` increments the shared counter and stores the stream in the appropriate cache. `invalidate` checks the input cache first, then the output cache, invalidates the entry, and returns the stream that was removed. State is process-local and in-memory; stream lifetime is tied to cache access, explicit close, and Guava eviction.

## Dependencies and Integration Points
The class integrates with proxy REST handlers: `PathsRestServiceHandler.createFile` and `openFile` insert streams, and `StreamsRestServiceHandler` reads, writes, and closes them. It depends on Alluxio filesystem stream types and Guava cache.

## Risks
The counter is an `int`, so very long-lived proxies could eventually wrap IDs. Input and output caches share the same counter but are separate maps, so an ID collision after wrap could be ambiguous. Removal listener exceptions are logged but not surfaced to callers. Cache eviction closes streams asynchronously from the caller's perspective, so clients holding stale IDs receive "stream does not exist."

## Test Signals
Relevant tests should verify ID uniqueness, explicit invalidation closes streams, expiration closes idle streams, and read/write handlers return errors for invalid or expired IDs.

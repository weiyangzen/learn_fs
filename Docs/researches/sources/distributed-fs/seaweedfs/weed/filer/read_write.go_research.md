# sources/distributed-fs/seaweedfs/weed/filer/read_write.go

## Purpose

`read_write.go` provides small client helpers for reading and writing filer entries through gRPC. It handles both inline entry content and chunk-backed content for reads, and create-or-update behavior for inline content writes.

## Important APIs, Types, and Functions

`ReadEntry` looks up an entry and writes either inline content or streamed chunk content into a buffer. `ReadInsideFiler` returns only inline entry content. `SaveInsideFiler` creates or updates an inline-content entry.

## Control Flow

`ReadEntry` calls `LookupEntry`; if `Entry.Content` is non-empty it writes directly to the buffer, otherwise it calls `StreamContent` over the entry chunks for the computed file size. `SaveInsideFiler` looks up the target; on `ErrNotFound` it creates a new file entry with timestamps, mode, file size, and inline content. On success it mutates the existing entry's content, mtime, and file size and sends `UpdateEntry`.

## State and Persistence Behavior

Persistence is remote through filer RPCs. Inline content is stored directly in the filer entry metadata, while chunk-backed reads stream from volume servers through `StreamContent`. `SaveInsideFiler` does not manage chunks; it stores small content inline.

## Dependencies and Integration Points

The file depends on filer protobuf lookup/create/update helpers, `wdclient.MasterClient`, `StreamContent`, and `FileSize`. It is used by internal code that stores small control/config files in the filer namespace.

## Risks and Edge Cases

`ReadInsideFiler` ignores chunk-backed content and returns only inline bytes. `SaveInsideFiler` does not handle lookup errors other than not found. Updating inline content on an entry that previously had chunks may leave chunk fields unchanged unless `UpdateEntry` semantics clear or ignore them upstream.

## Test Signals

Tests should cover inline read, chunk-stream read, create on missing entry, update existing inline content, non-not-found lookup errors, and behavior on existing chunk-backed entries.

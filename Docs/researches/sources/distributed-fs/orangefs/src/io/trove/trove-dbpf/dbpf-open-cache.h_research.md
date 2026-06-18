# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-open-cache.h

## Purpose
Declares the DBPF bstream open-cache API and open-reference types used by bstream operations.

## Important APIs, Types, And Functions
Defines `enum open_cache_open_type` with buffered/direct read/write modes, `struct open_cache_ref` containing fd, type, and internal cache pointer, plus declarations for initialize/finalize/get/put/remove and `clear_stranded_bstreams`.

## Control Flow
Bstream callers request an fd with `dbpf_open_cache_get`, perform I/O, return it with `dbpf_open_cache_put`, and call `dbpf_open_cache_remove` when deleting a bstream. Management calls initialization/finalization and stranded cleanup during backend lifecycle.

## State And Persistence
No state is stored in the header. It exposes references to an implementation-managed in-memory cache and functions that affect persistent bstream files.

## Dependencies And Integration Points
Includes TROVE and internal DBPF types. It is consumed by bstream code and management initialization/lookup/finalization paths.

## Risks And Test Signals
Risks center on callers mishandling `open_cache_ref.internal`, mismatched get/put pairs, or using a reference after remove/finalize. Compile coverage and bstream I/O/remove integration tests are the key signals.

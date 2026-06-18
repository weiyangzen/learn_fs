# sources/distributed-fs/orangefs/src/io/buffer/ncac-interface.h

## Purpose
Declares the external NCAC buffer-cache interface, public descriptor/handle/reply types, operation codes, and cache hints.

## Important APIs, Types, And Functions
Defines `NCAC_READ`, `NCAC_WRITE`, `NCAC_BUF_READ`, `NCAC_BUF_WRITE`, `NCAC_QUERY`, `NCAC_DEMOTE`, and `NCAC_SYNC`; `cache_hints_t`; `cache_desc_t`; `cache_read_desc_t`; `cache_write_desc_t`; `cache_sync_desc_t`; `cache_request_t`; `cache_reply_t`; and `cache_info_t`. Declares post/test/done functions and `cache_query_info`.

## Control Flow
Callers fill read/write descriptors with collection, handle, context, stream offset/size arrays, optional user buffer, length, and cache hints. The API returns a request handle and, when data buffers are ready, a reply vector of cache buffer addresses, sizes, and flags.

## State And Persistence
The header defines public in-memory contracts only. `cache_request_t.internal_id` is explicitly internal and should not be modified by callers.

## Dependencies And Integration Points
Includes `pvfs2-types.h` and bridges server/network I/O code to NCAC internals. Its operation codes must match `NCAC_do_a_job` dispatch.

## Risks And Test Signals
Risks include duplicate descriptor structs, comments referencing status names not defined in this header, and `cache_query_info` declaration without an implementation in the listed source files. API tests should verify descriptor layout, request-handle lifecycle, and build/link coverage for declared functions.

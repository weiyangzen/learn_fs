# sources/distributed-fs/orangefs/src/io/description/pint-request-encode.h

## Purpose
Provides inline helpers to encode and decode `PINT_Request` trees by linearizing nested request structures into a contiguous array with pointer fields represented as encoded offsets/integers.

## Important APIs, Types, And Functions
Defines `PVFS_REQ_LIMIT_PINT_REQUEST_NUM` as 100. Inline functions are `linearize_PVFS_Request`, `encode_PVFS_Request_fields`, `encode_linearized_PVFS_Request`, `encode_PINT_Request`, and `decode_PINT_Request`.

## Control Flow
Encoding verifies nested request count, allocates a linearized request array, commits the request tree into it, encodes pointer fields into relocatable form, writes the nested count and all request fields, then frees the temporary array. Decoding reads the nested count, allocates an array, decodes scalar fields, stores encoded `ereq`/`sreq` integers into pointer fields, and leaves final pointer repair to `PINT_Request_decode`.

## State And Persistence
No global state exists. Encoded buffers persist request layout for transport/storage. Decode uses `decode_malloc`; callers must later free through the request decode/free path.

## Dependencies And Integration Points
Depends on PVFS encode/decode helpers, `PINT_request_commit`, `PINT_request_encode`, `PINT_Request_decode`, and request struct definitions from including context. Included by `pint-request.h`.

## Risks And Test Signals
Risks include the hard nesting limit of 100, encoding pointer offsets through 32-bit integers via `uintptr_t` casts, allocation/free family consistency (`decode_malloc` with `free` or `decode_free`), and reliance on later pointer fix-up. Tests should encode/decode nested request trees at boundaries, invalid over-limit trees, 64-bit builds, and request structures with multiple `ereq`/`sreq` relationships.

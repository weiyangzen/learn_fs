# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/auth_gss_internal.h

## Purpose
This internal header provides small parsing helpers used by RPCSEC_GSS client code to decode gssd downcall byte streams safely. It keeps low-level length and bounds checks shared and local to the auth_gss implementation.

## Important APIs, Types, and Functions
`simple_get_bytes()` copies a fixed-size value from a cursor to a destination and returns the advanced cursor or `ERR_PTR(-EFAULT)` on overflow or pointer wrap. `simple_get_netobj_noprof()` reads an unsigned length, validates the following variable-length data, duplicates it with `kmemdup_noprof()`, and fills an `xdr_netobj`. `simple_get_netobj` is an `alloc_hooks()` wrapper around the noprof implementation.

## Control Flow
Callers pass a current pointer and an end pointer. Fixed fields are consumed first; variable fields read a length then allocate and copy the payload. `auth_gss.c` uses these helpers in `gss_fill_context()` and downcall parsing to decode timeout, window, opaque wire context, imported security context length, and optional acceptor name.

## State and Persistence
The header owns no persistent state. It allocates copied netobject data that callers must free, typically as part of `gss_cl_ctx` cleanup.

## Dependencies and Integration Points
It depends on Linux error pointers, string/memory helpers, XDR netobject definitions, allocation hooks, and `GFP_KERNEL`. It integrates with gssd downcall import, but is not a public kernel API.

## Risks and Edge Cases
The helpers defend against buffer overrun and pointer wrap, which is important because downcalls originate from user space. `simple_get_netobj_noprof()` can leave prior allocations to caller cleanup if a later field fails. The length type is an unsigned int in host byte order, matching the local pipe protocol rather than external XDR.

## Test Signals
There are no direct tests. Malformed gssd downcalls, zero-length netobjects, and oversized length fields are the practical coverage targets.

# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-context.h

## Purpose
`dbpf-context.h` declares DBPF context open/close entry points for the Trove context method implementation.

## Important APIs, types, and functions
It declares `dbpf_open_context(TROVE_coll_id, TROVE_context_id *)` and `dbpf_close_context(TROVE_coll_id, TROVE_context_id)`.

## Control flow and state
No state is defined in the header. It wraps declarations in `extern "C"` for C++ compatibility.

## Persistence and integration
Contexts are runtime-only completion domains. The header lets method-table setup and DBPF internals bind to the context implementation.

## Dependencies
It includes `pvfs2-internal.h` and `trove-types.h`.

## Risks and test signals
The declaration surface is small. Build tests should ensure context methods remain signature-compatible with `struct TROVE_context_ops`; runtime tests belong to `dbpf-context.c`.

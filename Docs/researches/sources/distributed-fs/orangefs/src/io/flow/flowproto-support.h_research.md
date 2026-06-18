# sources/distributed-fs/orangefs/src/io/flow/flowproto-support.h

Purpose: defines the internal protocol operations table used by the flow subsystem to call concrete flow protocol implementations.

Important APIs/types: `struct flowproto_ops` has protocol name and function pointers for initialize, finalize, getinfo, setinfo, post, and cancel. `struct flowproto_type_support` describes supported source/destination endpoint ids for query-style protocols.

Integration: `flow.c` builds an active table of `flowproto_ops` and delegates post/cancel/info calls. Multiqueue and cache protocols conform to this current six-operation shape; template and dump-offsets sources appear to use an older extended shape.

Risks/test signals: this header is a central ABI between core flow and protocols. Any protocol initializer with too many fields is a compile-time signal of stale code. Tests should compile all enabled static protocols and verify cancel pointer nullability is handled by `PINT_flow_cancel()`.

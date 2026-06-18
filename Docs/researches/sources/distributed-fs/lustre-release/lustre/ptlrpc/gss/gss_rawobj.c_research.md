# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_rawobj.c

Purpose: implements raw object allocation, duplication, serialization, extraction, netobj conversion, and fixed byte extraction for GSS token/context parsing.

Important APIs/types/functions: `rawobj_empty()`, `rawobj_alloc()`, `rawobj_free()`, `rawobj_equal()`, and `rawobj_dup()` manage `rawobj_t` ownership. `rawobj_serialize()` writes a little-endian length followed by 4-byte-rounded data. `rawobj_extract()`, `_alloc()`, `_local()`, and `_local_alloc()` parse serialized objects either by pointing into the caller buffer or allocating a copy, with network little-endian or local-endian length handling. `rawobj_from_netobj()` and `_alloc()` bridge `netobj_t`. `buffer_extract_bytes()` copies fixed-size fields and advances a pointer.

Control flow: serializers and extractors validate remaining buffer length before consuming bytes. Extractors set empty objects to `{0,NULL}` and either point into the serialized stream or allocate independent storage. Local extraction uses exact length rather than network 4-byte rounding.

State/persistence: allocated raw object data is caller-owned until `rawobj_free()`. Non-alloc extractors borrow the backing buffer.

Dependencies/integration: heavily used by GSS keyring downcalls, context import parsers, client upcall packing, and service upcall handling.

Risks/test signals: caller confusion between borrowed and allocated raw objects can cause lifetime bugs. `rawobj_serialize()` copies `obj->data` even for nonzero len and assumes valid data. Tests should cover empty objects, short buffers, rounded network lengths, local unrounded lengths, allocation failure, duplicate/free idempotence expectations, endianness, and pointer/buflen advancement.

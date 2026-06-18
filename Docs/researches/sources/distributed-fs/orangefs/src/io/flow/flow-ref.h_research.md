# sources/distributed-fs/orangefs/src/io/flow/flow-ref.h

Purpose: declares the flow endpoint-pair to protocol-id mapping structure and functions.

Important APIs/types: `struct flow_ref_entry` stores `src_endpoint`, `dest_endpoint`, `flowproto_id`, and a quicklist link. `flow_ref_p` is a list head pointer. Functions manage lifecycle, insert, search, remove, and cleanup.

Integration: included by `flow.c` for global protocol mapping cache. Endpoint enum values come from `flow.h`.

Risks/test signals: caller ownership after `flow_ref_remove()` is not documented in the header. Tests should validate mapping behavior and cleanup ownership before this API is used in new routing code.

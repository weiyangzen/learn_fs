# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/gct.h

This header defines Galaxy Configuration Tree v6 node structures and search plumbing. `gct6_node` captures firmware tree node metadata including type/subtype, ownership, IDs, links, flags, FRU id, checksum, and magic. `gct6_search_struct` pairs a type/subtype with a callback.

Important macros are `GCT_NODE_MAGIC`, `GCT_TYPE_HOSE`, `GCT_SUBTYPE_IO_PORT_MODULE`, and `GCT_NODE_PTR`, which resolves a firmware tree offset relative to `hwrpb->frut_offset`. `gct6_find_nodes` is declared for walking/searching nodes.

State is firmware FRU/configuration tree data reachable from HWRPB. Integration is platform discovery, especially hose/I/O module enumeration. Risks are trusting firmware offsets, checksum/magic validation, and pointer arithmetic against HWRPB. Tests are build coverage and platform discovery on systems exposing GCT/FRU data.

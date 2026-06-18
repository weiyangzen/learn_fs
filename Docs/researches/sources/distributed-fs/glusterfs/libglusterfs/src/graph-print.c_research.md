# sources/distributed-fs/glusterfs/libglusterfs/src/graph-print.c

Purpose: `graph-print.c` serializes an in-memory `glusterfs_graph_t` back into volfile-like text.

Important APIs and types: `struct gf_printer` abstracts writes and tracks length. `gp_write_file` writes to `FILE *`; `gpprintf` formats with `gf_vasprintf` and writes through the printer. `_print_volume_options` emits `option key value` lines. `glusterfs_graph_print` prints volumes in reverse linked-list order, including type, options, subvolumes, and `end-volume`. `glusterfs_graph_print_file` is the public file-backed entry point.

Control flow and state: printing starts from `graph->first`, walks to the linked-list tail, then walks backward through `prev` so subvolumes appear before parents as volfile syntax expects. Options are printed via `dict_foreach`; child links are printed in list order. The printer length accumulates successful writes.

Dependencies and integration: depends on common utils, xlator graph structures, graph-utils declarations, dict iteration, logging, and GF allocation. It complements `graph.y`/`graph.l` parsing.

Risks: dictionary iteration order may not preserve original option ordering, so output may be semantically equivalent but not text-identical. Values are printed unquoted, which can be unsafe for whitespace/special characters. `fwrite(buf, len, 1)` treats partial writes as failure.

Test signals: round-trip parse/print/parse tests, options containing spaces or quotes, multi-child graphs, empty graph printing, fwrite failure injection, and deterministic output expectations should be covered.

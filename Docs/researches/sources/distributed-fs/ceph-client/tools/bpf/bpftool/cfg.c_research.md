<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.c

Purpose: this file builds and prints a Graphviz DOT control-flow graph for translated eBPF instructions. It is used by bpftool's xlated dump path when graph output is requested.

Important APIs/types/functions: internal graph types are `struct cfg`, `struct func_node`, `struct bb_node`, and `struct edge_node`. `cfg_partition_funcs()` finds BPF-to-BPF subprogram starts from pseudo-call targets. `func_partition_bb_head()`, `func_partition_bb_tail()`, and `func_add_special_bb()` partition each function into basic blocks plus ENTRY/EXIT nodes. `func_add_bb_edges()` adds fallthrough and jump edges. `cfg_dump()` emits DOT, and public `dump_xlated_cfg()` builds, dumps, and destroys the graph.

Control flow: `dump_xlated_cfg()` treats the input byte buffer as `struct bpf_insn[]`, initializes a `cfg`, partitions functions, partitions each function into basic blocks, adds entry/exit and edges, prints DOT subgraphs per function, then frees all nodes and edges. Blocks start at function start, jump targets, and conditional fallthroughs. Basic block tails are computed from the next block head or function end.

State and persistence: all graph state is heap-allocated and freed in `cfg_destroy()`. Output is written to stdout as DOT. It does not mutate kernel or bpftool state.

Dependencies and integration points: it depends on Linux list helpers, eBPF instruction macros, bpftool error reporting, and `dump_xlated_for_graph()` from the xlated dumper to render instructions inside record-shaped nodes. The header `cfg.h` exposes only `dump_xlated_cfg()`.

Risks: pointer arithmetic assumes jump targets and pseudo-call targets are valid within the provided instruction buffer; invalid buffers can produce missing destination blocks or undefined behavior. Error paths during graph construction may return without freeing partially allocated graph state because `cfg_destroy()` is called only after successful build in `dump_xlated_cfg()`. DOT labels rely on the xlated dumper to escape instruction text. The predecessor edge list is only populated for exit's incoming edge; most graph traversal uses successor lists, so this is enough for output but not a complete bidirectional graph.

Test signals: graph tests should cover straight-line programs, unconditional jumps, conditional jumps, exits, calls/subprograms, line info/opcode options, invalid jump targets, empty buffers, and DOT rendering accepted by Graphviz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/cfg.c -->

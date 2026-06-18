# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/xlator.h

Purpose: `xlator.h` is the central translator ABI/API definition. It defines locations, all filesystem operation callback and call signatures, fop tables, translator callback/dump operations, the `xlator_t` runtime object, and the exported `xlator_api_t` module contract.

Important APIs and types: `loc_t` carries path/name/inode/parent and GFIDs. Dozens of `fop_*_t` and `fop_*_cbk_t` typedefs define the async filesystem ABI. `struct xlator_fops` must match `glusterfs-fops.x` ordering and contains callback entries after call entries for `STACK_WIND` type checking. `struct xlator_cbks` handles inode/fd/client lifecycle callbacks. `struct xlator_dumpops` supports statedump. `struct _xlator` stores graph links, options, dlopen handles, fops/cbks/dumpops, init/fini/reconfigure hooks, stats, context, inode table, mem accounting, multiplexing IDs, cleanup flags, and topology metadata. `xlator_api_t` is the module export.

Control flow and state: graph parsing fills name/type/options/child links. Dynamic loading fills function tables and hooks. Stack macros call fops through these tables, while graph lifecycle calls init/reconfigure/fini/notify. Per-fop atomic stats and latency live inside each translator.

Dependencies and integration: this header ties together dicts, iobufs, stacks, options, clients, latency, globals, and graph management. `graph.c`, `options.h`, `stack.h`, and `syncop.h` all depend on its layout.

Risks: ABI stability is critical: fop order, `volume_option_t`, and `xlator_api_t` layout are externally constrained. The scanned source shows duplicated prototype text in this header, which should be watched by builds. `cleanup_starting`, notify, and multiplexing fields are race-sensitive.

Test signals: translator module load/init/fini tests, fop index/stat correctness, graph topology traversal, option validation, pass-through fop dispatch, multiplex attach/detach, loc copy/wipe behavior, and ABI/layout checks are high-value.

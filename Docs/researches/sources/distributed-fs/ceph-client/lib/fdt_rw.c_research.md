# sources/distributed-fs/ceph-client/lib/fdt_rw.c

## Purpose
Kernel wrapper for shared libfdt read-write mutation routines. It includes the kernel environment and compiles `../scripts/dtc/libfdt/fdt_rw.c`.

## Important APIs, Types, and Functions
The included code provides mutable FDT APIs such as `fdt_add_mem_rsv()`, `fdt_del_mem_rsv()`, `fdt_set_name()`, `fdt_setprop_placeholder_namelen()`, `fdt_setprop_namelen()`, `fdt_appendprop()`, `fdt_delprop()`, `fdt_add_subnode_namelen()`, `fdt_add_subnode()`, `fdt_del_node()`, `fdt_open_into()`, and `fdt_pack()`. Internal helpers splice memory reservation, structure, and string blocks.

## Control Flow
Before mutating, the included implementation probes blob layout and writability. Mutation paths resize or add properties, append strings, splice structure-block data, add/delete nodes, and repack FDT blocks. `fdt_open_into()` can reorganize a blob into a writable buffer, and `fdt_pack()` compacts it.

## State and Persistence
No globals are owned by the wrapper. Persistent effects are direct modifications to the caller's FDT buffer, including header fields, structure block, strings block, and reserve map.

## Dependencies and Integration Points
Depends on core, read-only, and environment libfdt helpers. It integrates with boot/platform code that edits firmware-provided trees or constructs adjusted trees before handing them to later consumers.

## Risks
Mutation is buffer-layout-sensitive. Incorrect splice sizes or no-space handling can corrupt an FDT. String-block deduplication/removal must preserve referenced property names. Shared-source updates are imported wholesale. Callers must not pass read-only or undersized buffers to write APIs.

## Test Signals
Exercise add/delete reservations, rename nodes, set/append/delete properties, add/delete subnodes, open into larger buffers, pack after deletion, no-space paths, and validation with read-only lookup after each mutation.

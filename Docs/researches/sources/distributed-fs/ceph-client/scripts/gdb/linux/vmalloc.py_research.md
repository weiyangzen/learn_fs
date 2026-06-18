# sources/distributed-fs/ceph-client/scripts/gdb/linux/vmalloc.py

## Purpose
`vmalloc.py` implements `lx-vmallocinfo`, a GDB view of busy vmalloc/vmap areas similar to `/proc/vmallocinfo`.

## Important APIs, Types, and Functions
`is_vmalloc_addr()` uses `mm.page_ops()` to compare tag-reset addresses against architecture `VMALLOC_START/END`. `LxVmallocInfo.invoke()` walks `vmap_nodes[i].busy.head` and formats either `vm_map_ram` areas or full `struct vm_struct` metadata.

## Control Flow
The command requires `CONFIG_MMU`, iterates all `nr_vmap_nodes`, walks each busy list, prints ranges, size, caller, page count, physical address, flags, and whether `pages` itself is vmalloc-backed.

## State and Persistence Behavior
Read-only. It reflects current vmap allocator state without synchronization.

## Dependencies and Integration Points
It depends on list traversal, vmalloc constants, and memory-layout helpers from `mm.py`.

## Risks and Test Signals
The vmap node layout is kernel-version sensitive. Corrupt busy lists or stale `vm` pointers can break formatting. Test by comparing with `/proc/vmallocinfo`, including `ioremap`, `vmalloc`, `vmap`, `usermap`, and `vm_map_ram` entries.

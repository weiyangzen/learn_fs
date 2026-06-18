# sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_debugfs.c

## Purpose
`kexec_handover_debugfs.c` exposes KHO incoming and outgoing metadata through debugfs. It lets developers inspect root FDT blobs, preserved subtree blobs, and scratch region physical addresses/sizes.

## Important APIs, Types, and Functions
Global `debugfs_root` is `/sys/kernel/debug/kho`. Internal `struct fdt_debugfs` stores list linkage, `debugfs_blob_wrapper`, and dentry. Public helpers are `kho_debugfs_init()`, `kho_in_debugfs_init()`, `kho_out_debugfs_init()`, `kho_debugfs_blob_add()`, and `kho_debugfs_blob_remove()`. Show helpers are `scratch_phys_show()` and `scratch_len_show()`.

## Control Flow
`kho_debugfs_init()` creates the root directory. `kho_out_debugfs_init()` creates `out`, `out/sub_fdts`, and readonly files for scratch physical addresses and lengths. `kho_in_debugfs_init()` creates `in`, exposes the incoming root FDT as a blob, walks FDT subnodes, validates subtree pointer and size properties, maps them with `phys_to_virt()`, and exposes each as a blob under `in/sub_fdts`.

`kho_debugfs_blob_add()` chooses either the root KHO debugfs directory or `sub_fdts` and creates a blob wrapper; `kho_debugfs_blob_remove()` removes the matching wrapper by data pointer.

## State and Persistence Behavior
Debugfs state is runtime-only and mirrors live KHO FDT pointers. Blob wrappers point directly at preserved or allocated FDT memory; they do not copy blob contents. Entries are removed when subtrees are removed or recursively if init fails.

## Dependencies and Integration Points
It depends on debugfs, libfdt, KHO ABI property names, `phys_to_virt()`, and scratch globals from KHO core. It is called by KHO init and subtree add/remove paths when `CONFIG_KEXEC_HANDOVER_DEBUGFS` is enabled.

## Risks and Test Signals
Debugfs exposes raw handover metadata to root and can show stale data if blobs are freed without removal. Incoming subtree validation must tolerate malformed FDT nodes. Tests should mount debugfs and verify `kho/out/fdt`, `out/sub_fdts`, scratch files, incoming FDT blobs after KHO boot, subtree add/remove cleanup, and debugfs-disabled inline stubs.

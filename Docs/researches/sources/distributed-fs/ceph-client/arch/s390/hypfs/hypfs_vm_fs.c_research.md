<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm_fs.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm_fs.c

Purpose: Converts z/VM DIAG 2FC records into the mounted hypfs directory tree.

Important APIs/types/functions: Defines helper macro `ATTRIBUTE()`, `hypfs_vm_create_guest()`, and public `hypfs_vm_create_files()`.

Control flow: `hypfs_vm_create_files()` obtains a DIAG 2FC snapshot using the query selected in `hypfs_vm.c`, creates `/hyp/type` as "z/VM Hypervisor", creates `/cpus/count` from logical CPU data, creates `/systems`, and iterates all guest records. `hypfs_vm_create_guest()` converts the guest name from EBCDIC, creates per-guest directories, writes online time, CPU timing/capping/dedication/count/weight attributes, memory min/max/used/share attributes, and scheduler sample counters.

State and persistence: The DIAG 2FC snapshot is temporary and freed after tree creation. The generated hypfs tree persists until the next filesystem update/rebuild.

Dependencies and integration points: Depends on `hypfs_vm.c` collection, `hypfs.h` inode creation helpers, EBCDIC conversion, and mounted hypfs update flow in `inode.c`.

Risks: Field naming is partly ABI-frozen; the source notes `weight_min` is historically misnamed and actually contains operating CPU count. Guest names after trimming must be valid unique directory names. Errors during tree creation must free the snapshot.

Test signals: Mounted hypfs on z/VM with multiple guests, EBCDIC guest-name conversion, CPU/memory/sample value validation against DIAG 2FC, duplicate or blank guest-name handling, and update-path failure injection.

Source read size: 134 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm_fs.c -->

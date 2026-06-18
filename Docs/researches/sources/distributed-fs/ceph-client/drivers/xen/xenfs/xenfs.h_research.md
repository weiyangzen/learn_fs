<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenfs.h -->
# sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenfs.h

## Purpose
`xenfs.h` is the small internal header connecting the xenfs superblock code with optional file-operation implementations.

## Important APIs, types, and functions
It declares `xsd_kva_file_ops`, `xsd_port_file_ops`, and `xensyms_ops`.

## Control flow
The header has no executable flow. `super.c` uses the declarations when creating initial-domain tree descriptors.

## State and persistence
No state is defined. The declarations refer to synthetic runtime files.

## Dependencies and integration points
It depends on `struct file_operations` being visible to including C files and bridges `super.c` to `xenstored.c` and `xensyms.c`.

## Risks and test signals
Risks are config mismatches where declarations are referenced but objects are not linked. Test signals are `CONFIG_XEN_DOM0` and `CONFIG_XEN_SYMS` build combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenfs.h -->

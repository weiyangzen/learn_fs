<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.h -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.h

Purpose: Defines the z/VM DIAG 2FC data model and helper declarations shared by raw debugfs and mounted hypfs formatting code.

Important APIs/types/functions: Defines `DIAG2FC_NAME_LEN`, `struct diag2fc_data`, `struct diag2fc_parm_list`, `diag2fc_store()`, `diag2fc_free()`, and extern `diag2fc_guest_query`.

Control flow: Header only; no runtime control flow.

State and persistence: `struct diag2fc_data` describes persisted snapshot records: CPU times, elapsed time, memory limits/usage/share, physical/logical/virtual CPU counts, CPU weights/samples, and EBCDIC guest name. `diag2fc_guest_query` state is defined in `hypfs_vm.c`.

Dependencies and integration points: Included by `hypfs_vm.c` and `hypfs_vm_fs.c`. The structure layout must match z/VM DIAG 2FC format.

Risks: Layout changes would break hypervisor ABI parsing and raw debugfs consumers. Fields are fixed-width and endian/encoding sensitive.

Test signals: Compile checks for both VM files, raw DIAG 2FC size/count validation, and mounted hypfs value checks against z/VM data.

Source read size: 50 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag_fs.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag_fs.c

Purpose: Converts LPAR DIAG 204 and DIAG 224 data into the mounted hypfs directory tree.

Important APIs/types/functions: Defines many accessors that abstract simple and extended DIAG 204 formats, including info-block, partition-header, CPU-info, physical-header, and physical-CPU getters. Key functions are `hypfs_create_cpu_files()`, `hypfs_create_lpar_files()`, `hypfs_create_phys_cpu_files()`, `hypfs_create_phys_files()`, `hypfs_diag_create_files()`, `diag224_idx2name()`, `diag224_get_name_table()`, `diag224_delete_name_table()`, `__hypfs_diag_fs_init()`, and `__hypfs_diag_fs_exit()`.

Control flow: Init fetches the DIAG 224 CPU type name table on LPAR machines. `hypfs_diag_create_files()` gets and refreshes the DIAG 204 buffer, creates `/systems`, iterates partition records to create per-LPAR CPU directories and timing/type files, optionally creates physical CPU files when DIAG 204 flags include physical data, then creates `/hyp/type` as "LPAR Hypervisor".

State and persistence: `diag224_cpu_names` is a single DMA-capable page retained until exit. The mounted hypfs tree is reconstructed by the inode layer on update and stores generated file contents as dentries/inodes.

Dependencies and integration points: Uses `hypfs_diag.c` for DIAG 204 storage, `hypfs.h` inode helpers, DIAG 224 for CPU type names, EBCDIC-to-ASCII conversion, and machine type detection.

Risks: Pointer arithmetic over firmware DIAG 204 buffers must match selected simple/extended struct sizes. DIAG 224 index conversion assumes the name table is present and large enough. A historical naming mistake is preserved: `weight_min` actually represents operating CPUs in the z/VM file path, not here.

Test signals: Mounted hypfs on LPAR with simple and extended DIAG 204 data, DIAG 224 unavailable failures, physical CPU section presence/absence, EBCDIC name trimming, and tree update tests.

Source read size: 377 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag_fs.c -->

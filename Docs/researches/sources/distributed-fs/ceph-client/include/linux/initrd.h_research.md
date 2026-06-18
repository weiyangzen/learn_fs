<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/initrd.h -->
# sources/distributed-fs/ceph-client/include/linux/initrd.h

Purpose: Declares initrd/initramfs global state and helpers.

Important APIs/types/functions: Externs include `initrd_start`, `initrd_end`, `initrd_below_start_ok`, `initrd_start` resource ranges on some architectures, and `phys_initrd_start`/`phys_initrd_size`. Functions include `initrd_load()`, optional `initrd_memblock_reserve()`, `free_initrd_mem()`, and `early_initrdmem()` depending on configuration.

Control flow: Early boot records and reserves initrd memory; later rootfs/initramfs setup loads it and frees memory when allowed.

State/persistence: Initrd physical/virtual ranges persist during boot and may be freed after unpack/load.

Dependencies/integration: Integrates bootmem/memblock, rootfs, architecture boot protocols, and init memory freeing.

Risks: Incorrect range reservation can overwrite initrd or leak memory; physical/virtual address confusion is architecture-sensitive.

Test signals: Boot with and without initrd, high/low memory placement, memblock reservation logs, rootfs unpack success, and free-initrd memory accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/initrd.h -->

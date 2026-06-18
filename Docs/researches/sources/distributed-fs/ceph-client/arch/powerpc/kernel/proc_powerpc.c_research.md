# sources/distributed-fs/ceph-client/arch/powerpc/kernel/proc_powerpc.c

Purpose: this file creates PowerPC-specific `/proc` entries, especially the PPC64 `systemcfg` page and compatibility directory/symlink layout under `/proc/powerpc`, `/proc/ppc64`, and `/proc/rtas`.

Important APIs and state: under `CONFIG_PPC64_PROC_SYSTEMCFG`, `systemcfg_data_store` is a page-aligned union that backs exported `struct systemcfg *systemcfg`. `page_map_proc_ops` implements fixed-size seek, read, and mmap of exactly one page. `proc_ppc64_init()` fills `systemcfg` fields from PVR, firmware LPAR feature, memblock physical size, and cache descriptors, then creates `powerpc/systemcfg`. `proc_ppc64_create()` creates the `powerpc` root directory, the `ppc64` symlink on 64-bit, and RTAS directory/symlink when `/rtas` exists in the DT.

Control flow: `proc_ppc64_create()` is a `core_initcall`, so it runs early enough for later drivers to assume `/proc/powerpc` and optional RTAS paths exist. `proc_ppc64_init()` runs as an `__initcall` when configured and publishes the one-page systemcfg file after initializing content.

State and persistence: the systemcfg page persists for the lifetime of the kernel and may be read or mapped by user space. Proc dentries persist after init. The page contains static boot-time hardware and platform details rather than live counters.

Dependencies and integration points: depends on procfs, memblock, DT lookup for `/rtas`, firmware feature flags, RTAS headers, VDSO/systemcfg ABI definitions, and global cache descriptors. User-space compatibility is a key integration point because old PPC64 software may mmap `/proc/ppc64/systemcfg` through symlinked paths.

Risks: `page_map_mmap()` remaps a kernel physical page read-only by proc permissions but uses the VMA page protections supplied by the caller, so permission expectations rely on procfs open mode and mmap checks. The systemcfg ABI is fixed-size and compatibility-sensitive. Creation failures return nonzero but have limited recovery.

Test signals: boot should expose `/proc/powerpc`, `/proc/ppc64` on 64-bit, optional `/proc/powerpc/rtas`, optional `/proc/rtas`, and `powerpc/systemcfg` when configured. Read, seek, and one-page mmap should succeed; oversized mmap should return `-EINVAL`. Validate fields such as eye catcher, PVR, memory size, cache line sizes, and LPAR bit.

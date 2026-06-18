# sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/platsmp.c

Purpose: implements AST2600 SMP secondary boot through a shared secure boot memory region. Key functions are `aspeed_g6_smp_prepare_cpus`, `aspeed_g6_boot_secondary`, and the CPU method for `aspeed,ast2600-smp`.

Control flow caches the DT node `aspeed,ast2600-smpmem`, initializes the boot signature to `0xBADABABA`, and on boot maps the region, writes `secondary_startup_arm` physical address and a CPU-specific `0xABBAABxx` signature, sends `sev`, and unmaps. Persistent state is the retained DT node pointer. Dependencies include DT node mapping, secondary startup symbol, barriers, and Aspeed boot ROM/firmware polling protocol. Risks are missing node, mapping failures, stale node lifetime assumptions, and signature/address protocol mismatch. Test signals include CPU1 online on AST2600 and diagnostic logs for missing/mapping failures.

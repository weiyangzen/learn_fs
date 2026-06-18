<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_e500.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_e500.S

Purpose: Provides cache setup, idle-state setup, IVOR initialization wrappers, restore paths, and CPU-down cache flushing for e500/e500mc/e5500/e6500 BookE CPUs.

Important APIs/types/functions: `__e500_icache_setup`, `__e500_dcache_setup`, `setup_pw20_idle`, `setup_altivec_idle`, setup/restore entry points for e500v1/v2/e500mc/e5500/e6500, `flush_dcache_L1`, `has_L2_cache`, `flush_backside_L2_cache`, and `cpu_down_flush_*` routines.

Control flow: Setup enables/invalidate L1 caches, programs IVORs according to CPU/HV capability, enables idle controls, conditionally clears embedded-HV CPU feature bits if hardware lacks LPID support, and restores similar state after resume. CPU-down paths flush L1 and, where present, backside L2 before offlining.

State and persistence: Mutates L1CSR0/1, PWRMGTCR0, IVORs via external helpers, CPU feature flags, HID0 DCFA, L2CSR0, interrupt enable state, and cache contents.

Dependencies and integration points: Depends on BookE/e500 SPRs, nohash MMU definitions, MPC85xx SVR values, IVOR setup helpers, CPU spec offsets, and hotplug/power-management paths.

Risks: Cache flush loops depend on L1CFG geometry and known block sizes. Touching E.HV IVORs on unsupported CPUs is avoided by MMUCFG checks; breaking that can fault early.

Test signals: e500/e500mc/e5500/e6500 boot and CPU hotplug, cache coherency tests after offline, L2 skip on P2040, IVOR exception delivery, and suspend/restore coverage.

Source read size: 337 lines, 7107 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_e500.S -->

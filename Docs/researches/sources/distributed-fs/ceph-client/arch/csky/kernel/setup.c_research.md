# sources/distributed-fs/ceph-client/arch/csky/kernel/setup.c

Purpose: early command line, device tree, memblock, initrd, and architecture setup.

Important APIs/types/functions: functions: `setup_initrd`, `arch_zone_limits_init`, `csky_memblock_init`, `if`, `setup_arch`, `read_mmu_msa`, `csky_start`; exports: `va_pa_offset`

Control flow: Runtime flow is organized around `setup_initrd`, `arch_zone_limits_init`, `csky_memblock_init`, `if`, `setup_arch`, `read_mmu_msa`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/console.h`, `linux/memblock.h`, `linux/initrd.h`, `linux/of.h`, `linux/of_fdt.h`, `linux/start_kernel.h`, `linux/dma-map-ops.h`, `asm/sections.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

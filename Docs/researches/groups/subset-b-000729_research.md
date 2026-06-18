# Research: subset-b-000729

Grouped research for Ceph-client vendored Linux MIPS machine headers. Each delimited section is also written to the source-tree-aligned per-file research document required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_regs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_regs.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_regs.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 952 macros including `BCM63XX_REGS_H_`, `PERF_REV_REG`, `REV_CHIPID_SHIFT`, `REV_CHIPID_MASK`, `REV_REVID_SHIFT`, `REV_REVID_MASK`, `PERF_CKCTL_REG`, `CKCTL_3368_MAC_EN`, `CKCTL_3368_TC_EN`, `CKCTL_3368_US_TOP_EN`, `CKCTL_3368_DS_TOP_EN`, `CKCTL_3368_APM_EN`, `CKCTL_3368_SPI_EN`, `CKCTL_3368_USBS_EN`, `CKCTL_3368_BMU_EN`, `CKCTL_3368_PCM_EN`, `CKCTL_3368_NTP_EN`, `CKCTL_3368_ACP_B_EN`, `CKCTL_3368_ACP_A_EN`, `CKCTL_3368_EMUSB_EN`, `CKCTL_3368_ENET0_EN`, `CKCTL_3368_ENET1_EN`, `CKCTL_3368_USBU_EN`, `CKCTL_3368_EPHY_EN`, and 928 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `GPIO_MODE (56)`, `USBH_PRIV (22)`, `MPI_CSBASE (21)`, `CKCTL_6362 (20)`, `USBD_EVENT (19)`, `CKCTL_3368 (18)`, `CKCTL_6368 (18)`, `USBD_CSR (17)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral; the file contains 952 macros, so broad edits have high review cost and should be grouped by register block or bit-field family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_reset.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_reset.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_reset.h` provides machine-specific constants and declarations for `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__BCM63XX_RESET_H`; 0 structs: none; 1 enums: `bcm63xx_core_reset`; 1 callable helpers/prototypes: `bcm63xx_core_set_reset`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `bcm63xx_core_set_reset`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `bcm63xx_core_set_reset`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise the specific device path: RTC read/write, floppy DMA/IRQ, timer callbacks, or reset assertion/deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_timer.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_timer.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_timer.h` provides machine-specific constants and declarations for `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `BCM63XX_TIMER_H_`; 0 structs: none; 0 enums: none; 6 callable helpers/prototypes: `bcm63xx_timer_register`, `bcm63xx_timer_unregister`, `bcm63xx_timer_set`, `bcm63xx_timer_enable`, `bcm63xx_timer_disable`, `bcm63xx_timer_countdown`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `bcm63xx_timer_register`, `bcm63xx_timer_unregister`, `bcm63xx_timer_set`, `bcm63xx_timer_enable`, `bcm63xx_timer_disable`, `bcm63xx_timer_countdown`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `BCM63XX_TIMER (1)`. Typed contracts include no structs. Callable helpers or declarations include `bcm63xx_timer_register`, `bcm63xx_timer_unregister`, `bcm63xx_timer_set`, `bcm63xx_timer_enable`, `bcm63xx_timer_disable`, `bcm63xx_timer_countdown`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise the specific device path: RTC read/write, floppy DMA/IRQ, timer callbacks, or reset assertion/deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/board_bcm963xx.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/board_bcm963xx.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/board_bcm963xx.h` declares board, firmware, memory, and platform-data contracts for `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `BOARD_BCM963XX_H_`, `BCM963XX_CFE_VERSION_OFFSET`, `BCM963XX_NVRAM_OFFSET`; 6 structs: `board_info`, `bcm63xx_enet_platform_data`, `bcm63xx_enetsw_platform_data`, `bcm63xx_usbd_platform_data`, `gpio_led`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `board_info`, `bcm63xx_enet_platform_data`, `bcm63xx_enetsw_platform_data`, `bcm63xx_usbd_platform_data`, `gpio_led` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are `linux/types.h`, `linux/gpio.h`, `linux/leds.h`, `bcm63xx_dev_enet.h`, `bcm63xx_dev_usb_usbd.h`. Major macro families are `BCM963XX_CFE (1)`, `BCM963XX_NVRAM (1)`, `BOARD_BCM963XX (1)`. Typed contracts include `board_info`, `bcm63xx_enet_platform_data`, `bcm63xx_enetsw_platform_data`, `bcm63xx_usbd_platform_data`, `gpio_led`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/board_bcm963xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 39 macros including `__ASM_MACH_BCM963XX_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_4k_cache`, `cpu_has_fpu`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_vce`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_prefetch`, `cpu_has_mcheck`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `cpu_has_vtag_icache`, `cpu_has_dc_aliases`, `cpu_has_ic_fills_f_dc`, and 15 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are `bcm63xx_cpu.h`. Major macro families are `cpu_has (35)`, `_ (1)`, `cpu_dcache (1)`, `cpu_icache (1)`, `cpu_scache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/ioremap.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/ioremap.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/ioremap.h` provides platform hooks for deciding whether MMIO ranges need normal `ioremap()` on `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `BCM63XX_IOREMAP_H_`; 0 structs: none; 0 enums: none; 3 callable helpers/prototypes: `is_bcm63xx_internal_registers`, `plat_ioremap`, `plat_iounmap`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `is_bcm63xx_internal_registers`, `plat_ioremap`, `plat_iounmap`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `bcm63xx_cpu.h`. Major macro families are `BCM63XX_IOREMAP (1)`. Typed contracts include no structs. Callable helpers or declarations include `is_bcm63xx_internal_registers`, `plat_ioremap`, `plat_iounmap`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic `asm/io.h`, platform register windows, boot-time resource mapping, and driver MMIO accessors.

## Risks
incorrect range tests can double-map internal registers or skip cacheability/protection attributes for device memory; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/ioremap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `__ASM_MACH_BCM63XX_IRQ_H`, `NR_IRQS`, `MIPS_CPU_IRQ_BASE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `MIPS_CPU (1)`, `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/spaces.h` overrides virtual/physical address-space constants for `mach-bcm63xx`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `_ASM_BCM63XX_SPACES_H`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/bmips-spaces.h`, `asm/mach-generic/spaces.h`. Major macro families are `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-bmips`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 7 macros including `__ASM_MACH_BMIPS_CPU_FEATURE_OVERRIDES_H`, `cpu_has_vtag_icache`, `cpu_icache_snoops_remote_store`, `cpu_has_mips32r1`, `cpu_has_mips32r2`, `cpu_has_mips64r1`, `cpu_has_mips64r2`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (5)`, `_ (1)`, `cpu_icache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/ioremap.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/ioremap.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/ioremap.h` provides platform hooks for deciding whether MMIO ranges need normal `ioremap()` on `mach-bmips`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__ASM_MACH_BMIPS_IOREMAP_H`; 0 structs: none; 0 enums: none; 3 callable helpers/prototypes: `is_bmips_internal_registers`, `plat_ioremap`, `plat_iounmap`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `is_bmips_internal_registers`, `plat_ioremap`, `plat_iounmap`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `is_bmips_internal_registers`, `plat_ioremap`, `plat_iounmap`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic `asm/io.h`, platform register windows, boot-time resource mapping, and driver MMIO accessors.

## Risks
incorrect range tests can double-map internal registers or skip cacheability/protection attributes for device memory; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/ioremap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/spaces.h` overrides virtual/physical address-space constants for `mach-bmips`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `_ASM_BMIPS_SPACES_H`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/bmips-spaces.h`, `asm/mach-generic/spaces.h`. Major macro families are `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bmips/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-cavium-octeon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 34 macros including `__ASM_MACH_CAVIUM_OCTEON_CPU_FEATURE_OVERRIDES_H`, `cpu_dcache_line_size`, `cpu_icache_line_size`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_vce`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_prefetch`, `cpu_has_llsc`, `cpu_has_vtag_icache`, `cpu_has_dc_aliases`, `cpu_has_ic_fills_f_dc`, `cpu_has_64bits`, `cpu_has_octeon_cache`, `cpu_has_mips32r1`, `cpu_has_mips32r2`, `cpu_has_mips64r1`, `cpu_has_mips64r2`, `cpu_has_dsp`, and 10 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are `linux/types.h`, `asm/mipsregs.h`. Major macro families are `cpu_has (27)`, `ARCH_HAS (1)`, `MAX_DMA32 (1)`, `PREFETCH_STRIDE (1)`, `_ (1)`, `cpu_dcache (1)`, `cpu_hwrena (1)`, `cpu_icache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-cavium-octeon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 6 macros including `__OCTEON_IRQ_H__`, `NR_IRQS`, `MIPS_CPU_IRQ_BASE`, `OCTEON_IRQ_MSI_BIT0`, `OCTEON_IRQ_MSI_LAST`, `OCTEON_IRQ_LAST`; 0 structs: none; 1 enums: `octeon_irq`; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `OCTEON_IRQ (3)`, `MIPS_CPU (1)`, `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/kernel-entry-init.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/kernel-entry-init.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/kernel-entry-init.h` supplies machine-specific early-entry assembly hooks for `mach-cavium-octeon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 8 macros including `__ASM_MACH_CAVIUM_OCTEON_KERNEL_ENTRY_H`, `CP0_CVMCTL_REG`, `CP0_CVMMEMCTL_REG`, `CP0_PRID_REG`, `CP0_DCACHE_ERR_REG`, `CP0_PRID_OCTEON_PASS1`, `CP0_PRID_OCTEON_CN30XX`, `USE_KEXEC_SMP_WAIT_FINAL`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is assembly macro expansion during kernel entry. The common MIPS entry path invokes these macros before normal C setup, then returns to generic initialization after CP0, cache, TLB, or SMP wait-loop state has been prepared.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `CP0_PRID (3)`, `CP0_CVMCTL (1)`, `CP0_CVMMEMCTL (1)`, `CP0_DCACHE (1)`, `USE_KEXEC (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS reset/vector entry code, CP0 setup, TLB/cache mode selection, SMP secondary entry, and kexec handoff.

## Risks
assembly macros run before normal C runtime services, so register clobbers or CPU-revision checks can break boot very early; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot cold, kexec, and SMP secondary CPUs where supported, because failures can occur before console output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/kernel-entry-init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/mangle-port.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/mangle-port.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/mangle-port.h` customizes I/O port byte-lane/address swizzling for `mach-cavium-octeon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `__ASM_MACH_GENERIC_MANGLE_PORT_H`, `__should_swizzle_bits`; 0 structs: none; 0 enums: none; 2 callable helpers/prototypes: `__should_swizzle_bits`, `__should_swizzle_addr`; 1 extern variables: `octeon_should_swizzle_table`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `__should_swizzle_bits`, `__should_swizzle_addr`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm/byteorder.h`. Major macro families are `_ (2)`. Typed contracts include no structs. Callable helpers or declarations include `__should_swizzle_bits`, `__should_swizzle_addr`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic MIPS port I/O helpers, PCI/ISA-style drivers, bus endian translation, and platform-specific bridge windows.

## Risks
bad swizzle rules silently corrupt byte/word I/O against legacy devices; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/mangle-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/spaces.h` overrides virtual/physical address-space constants for `mach-cavium-octeon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 4 macros including `_ASM_MACH_CAVIUM_OCTEON_SPACES_H`, `CAC_BASE`, `UNCAC_BASE`, `IO_BASE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `linux/const.h`, `asm/mach-generic/spaces.h`. Major macro families are `CAC_BASE (1)`, `IO_BASE (1)`, `UNCAC_BASE (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cavium-octeon/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cobalt.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cobalt.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cobalt.h` declares board, firmware, memory, and platform-data contracts for `mach-cobalt`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `__ASM_COBALT_H`, `COBALT_BRD_ID_QUBE1`, `COBALT_BRD_ID_RAQ1`, `COBALT_BRD_ID_QUBE2`, `COBALT_BRD_ID_RAQ2`; 0 structs: none; 0 enums: none; 2 callable helpers/prototypes: `cobalt_machine_halt`, `cobalt_machine_restart`; 1 extern variables: `cobalt_board_id`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `cobalt_machine_halt`, `cobalt_machine_restart`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `COBALT_BRD (4)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `cobalt_machine_halt`, `cobalt_machine_restart`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cobalt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-cobalt`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 37 macros including `__ASM_COBALT_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_vce`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_prefetch`, `cpu_has_mcheck`, `cpu_has_ejtag`, `cpu_has_inclusive_pcaches`, `cpu_dcache_line_size`, `cpu_icache_line_size`, `cpu_scache_line_size`, `cpu_has_llsc`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_mdmx`, `cpu_has_mips3d`, and 12 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (32)`, `cpu_icache (2)`, `_ (1)`, `cpu_dcache (1)`, `cpu_scache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-cobalt`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 14 macros including `_ASM_COBALT_IRQ_H`, `I8259A_IRQ_BASE`, `PCISLOT_IRQ`, `MIPS_CPU_IRQ_BASE`, `GT641XX_CASCADE_IRQ`, `RAQ2_SCSI_IRQ`, `ETH0_IRQ`, `QUBE1_ETH0_IRQ`, `ETH1_IRQ`, `SERIAL_IRQ`, `SCSI_IRQ`, `I8259_CASCADE_IRQ`, `GT641XX_IRQ_BASE`, `NR_IRQS`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/irq_gt641xx.h`. Major macro families are `ETH0_IRQ (1)`, `ETH1_IRQ (1)`, `GT641XX_CASCADE (1)`, `GT641XX_IRQ (1)`, `I8259A_IRQ (1)`, `I8259_CASCADE (1)`, `MIPS_CPU (1)`, `NR_IRQS (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/mach-gt64120.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/mach-gt64120.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/mach-gt64120.h` provides machine-specific constants and declarations for `mach-cobalt`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `_COBALT_MACH_GT64120_H`, `GT64120_BASE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `GT64120_BASE (1)`, `_COBALT (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/mach-gt64120.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/bcsr.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/bcsr.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/bcsr.h` provides machine-specific constants and declarations for `mach-db1x00`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 139 macros including `_DB1XXX_BCSR_H_`, `DB1000_BCSR_PHYS_ADDR`, `DB1000_BCSR_HEXLED_OFS`, `DB1550_BCSR_PHYS_ADDR`, `DB1550_BCSR_HEXLED_OFS`, `PB1550_BCSR_PHYS_ADDR`, `PB1550_BCSR_HEXLED_OFS`, `DB1200_BCSR_PHYS_ADDR`, `DB1200_BCSR_HEXLED_OFS`, `PB1200_BCSR_PHYS_ADDR`, `PB1200_BCSR_HEXLED_OFS`, `DB1300_BCSR_PHYS_ADDR`, `DB1300_BCSR_HEXLED_OFS`, `BCSR_REG_WHOAMI`, `BCSR_REG_STATUS`, `BCSR_REG_SWITCHES`, `BCSR_REG_RESETS`, `BCSR_REG_PCMCIA`, `BCSR_REG_BOARD`, `BCSR_REG_LEDS`, `BCSR_REG_SYSTEM`, `BCSR_REG_INTCLR`, `BCSR_REG_INTSET`, `BCSR_REG_MASKCLR`, and 113 more; 0 structs: none; 2 enums: `bcsr_id`, `bcsr_whoami_boards`; 5 callable helpers/prototypes: `bcsr_init`, `bcsr_read`, `bcsr_write`, `bcsr_mod`, `bcsr_init_irq`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `bcsr_init`, `bcsr_read`, `bcsr_write`, `bcsr_mod`, `bcsr_init_irq`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `BCSR_RESETS (29)`, `BCSR_STATUS (27)`, `BCSR_BOARD (21)`, `BCSR_REG (16)`, `BCSR_SWITCHES (10)`, `BCSR_PCMCIA (8)`, `BCSR_SYSTEM (7)`, `BCSR_LEDS (5)`. Typed contracts include no structs. Callable helpers or declarations include `bcsr_init`, `bcsr_read`, `bcsr_write`, `bcsr_mod`, `bcsr_init_irq`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family; the file contains 139 macros, so broad edits have high review cost and should be grouped by register block or bit-field family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/bcsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-db1x00`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `__ASM_MACH_GENERIC_IRQ_H`, `MIPS_CPU_IRQ_BASE`, `NR_IRQS`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `MIPS_CPU (1)`, `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-db1x00/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-dec/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-dec/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-dec/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-dec`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 76 macros including `__ASM_MACH_DEC_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_tlbinv`, `cpu_has_segments`, `cpu_has_eva`, `cpu_has_htw`, `cpu_has_rixiex`, `cpu_has_maar`, `cpu_has_rw_llb`, `cpu_has_divec`, `cpu_has_prefetch`, `cpu_has_mcheck`, `cpu_has_ejtag`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `cpu_has_rixi`, `cpu_has_xpa`, `cpu_has_vtag_icache`, `cpu_has_ic_fills_f_dc`, `cpu_has_pindexed_dcache`, `cpu_icache_snoops_remote_store`, and 33 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (68)`, `cpu_icache (3)`, `cpu_dcache (2)`, `cpu_scache (2)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-dec/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-dec/mc146818rtc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-dec/mc146818rtc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-dec/mc146818rtc.h` adapts MC146818-compatible RTC accessors for `mach-dec`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 7 macros including `__ASM_MIPS_DEC_RTC_DEC_H`, `ARCH_RTC_LOCATION`, `RTC_PORT`, `RTC_IO_EXTENT`, `RTC_IOMAPPED`, `RTC_DEC_YEAR`, `RTC_ALWAYS_BCD`; 0 structs: none; 0 enums: none; 2 callable helpers/prototypes: `CMOS_READ`, `CMOS_WRITE`; 1 extern variables: `dec_rtc_base`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `CMOS_READ`, `CMOS_WRITE`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`, `asm/addrspace.h`, `asm/dec/system.h`. Major macro families are `ARCH_RTC (1)`, `RTC_ALWAYS (1)`, `RTC_DEC (1)`, `RTC_IO (1)`, `RTC_IOMAPPED (1)`, `RTC_PORT (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `CMOS_READ`, `CMOS_WRITE`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic RTC/CMOS code, platform I/O mapping, BCD/year handling, and machine time initialization.

## Risks
wrong address, data format, or year handling produces persistent clock drift or invalid wall time.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise the specific device path: RTC read/write, floppy DMA/IRQ, timer callbacks, or reset assertion/deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-dec/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__ASM_MACH_GENERIC_CPU_FEATURE_OVERRIDES_H`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/floppy.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/floppy.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/floppy.h` implements platform floppy controller I/O, DMA, IRQ, and memory helpers for `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `__ASM_MACH_GENERIC_FLOPPY_H`, `fd_free_irq`; 0 structs: none; 0 enums: none; 31 callable helpers/prototypes: `fd_inb`, `fd_outb`, `fd_enable_dma`, `fd_disable_dma`, `fd_request_dma`, `fd_free_dma`, `fd_clear_dma_ff`, `fd_set_dma_mode`, `fd_set_dma_addr`, `fd_set_dma_count`, `fd_get_dma_residue`, `fd_enable_irq`, `fd_disable_irq`, `fd_request_irq`, and 17 more; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `fd_inb`, `fd_outb`, `fd_enable_dma`, `fd_disable_dma`, `fd_request_dma`, `fd_free_dma`, `fd_clear_dma_ff`, `fd_set_dma_mode`, `fd_set_dma_addr`, `fd_set_dma_count`, and 21 more. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/delay.h`, `linux/ioport.h`, `linux/sched.h`, `linux/linkage.h`, `linux/types.h`, `linux/mm.h`, `asm/bootinfo.h`, `asm/cachectl.h`, `asm/dma.h`, `asm/floppy.h`, `asm/io.h`, `asm/irq.h`. Major macro families are `_ (1)`, `fd_free (1)`. Typed contracts include no structs. Callable helpers or declarations include `fd_inb`, `fd_outb`, `fd_enable_dma`, `fd_disable_dma`, `fd_request_dma`, `fd_free_dma`, `fd_clear_dma_ff`, `fd_set_dma_mode`, `fd_set_dma_addr`, `fd_set_dma_count`, `fd_get_dma_residue`, `fd_enable_irq`, and 19 more. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is legacy floppy block drivers, ISA DMA APIs, platform IRQ allocation, and low-memory DMA buffers.

## Risks
DMA residue/count handling and fixed IRQ/DMA assumptions are fragile on non-PC MIPS systems.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise the specific device path: RTC read/write, floppy DMA/IRQ, timer callbacks, or reset assertion/deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/floppy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/ioremap.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/ioremap.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/ioremap.h` provides platform hooks for deciding whether MMIO ranges need normal `ioremap()` on `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__ASM_MACH_GENERIC_IOREMAP_H`; 0 structs: none; 0 enums: none; 2 callable helpers/prototypes: `plat_ioremap`, `plat_iounmap`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `plat_ioremap`, `plat_iounmap`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `plat_ioremap`, `plat_iounmap`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic `asm/io.h`, platform register windows, boot-time resource mapping, and driver MMIO accessors.

## Risks
incorrect range tests can double-map internal registers or skip cacheability/protection attributes for device memory; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/ioremap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `__ASM_MACH_GENERIC_IRQ_H`, `NR_IRQS`, `I8259A_IRQ_BASE`, `MIPS_CPU_IRQ_BASE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `MIPS_CPU (2)`, `I8259A_IRQ (1)`, `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/kernel-entry-init.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/kernel-entry-init.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/kernel-entry-init.h` supplies machine-specific early-entry assembly hooks for `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__ASM_MACH_GENERIC_KERNEL_ENTRY_H`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is assembly macro expansion during kernel entry. The common MIPS entry path invokes these macros before normal C setup, then returns to generic initialization after CP0, cache, TLB, or SMP wait-loop state has been prepared.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS reset/vector entry code, CP0 setup, TLB/cache mode selection, SMP secondary entry, and kexec handoff.

## Risks
assembly macros run before normal C runtime services, so register clobbers or CPU-revision checks can break boot very early.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot cold, kexec, and SMP secondary CPUs where supported, because failures can occur before console output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/kernel-entry-init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/kmalloc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/kmalloc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/kmalloc.h` sets machine-specific DMA-safe `kmalloc` alignment for `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `__ASM_MACH_GENERIC_KMALLOC_H`, `ARCH_DMA_MINALIGN`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `ARCH_DMA (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is SLAB/SLUB allocation, DMA mapping assumptions, cache-line alignment, and platform device drivers.

## Risks
too-small alignment can expose DMA/cache aliasing bugs; too-large alignment wastes memory.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/kmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/mangle-port.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/mangle-port.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/mangle-port.h` customizes I/O port byte-lane/address swizzling for `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `__ASM_MACH_GENERIC_MANGLE_PORT_H`, `__swizzle_addr_b`, `__swizzle_addr_w`, `__swizzle_addr_l`, `__swizzle_addr_q`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (5)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic MIPS port I/O helpers, PCI/ISA-style drivers, bus endian translation, and platform-specific bridge windows.

## Risks
bad swizzle rules silently corrupt byte/word I/O against legacy devices.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/mangle-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/mc146818rtc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/mc146818rtc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/mc146818rtc.h` adapts MC146818-compatible RTC accessors for `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 4 macros including `__ASM_MACH_GENERIC_MC146818RTC_H`, `RTC_PORT`, `RTC_IRQ`, `RTC_ALWAYS_BCD`; 0 structs: none; 0 enums: none; 3 callable helpers/prototypes: `CMOS_READ`, `CMOS_WRITE`, `outb_p`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `CMOS_READ`, `CMOS_WRITE`, `outb_p`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm/io.h`. Major macro families are `RTC_ALWAYS (1)`, `RTC_IRQ (1)`, `RTC_PORT (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `CMOS_READ`, `CMOS_WRITE`, `outb_p`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic RTC/CMOS code, platform I/O mapping, BCD/year handling, and machine time initialization.

## Risks
wrong address, data format, or year handling produces persistent clock drift or invalid wall time.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise the specific device path: RTC read/write, floppy DMA/IRQ, timer callbacks, or reset assertion/deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/spaces.h` overrides virtual/physical address-space constants for `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 21 macros including `_ASM_MACH_GENERIC_SPACES_H`, `IO_SPACE_LIMIT`, `CAC_BASE`, `IO_BASE`, `UNCAC_BASE`, `MAP_BASE`, `HIGHMEM_START`, `CKSEG0ADDR_OR_64BIT`, `CKSEG1ADDR_OR_64BIT`, `TO_PHYS`, `TO_CAC`, `TO_UNCAC`, `PAGE_OFFSET`, `FIXADDR_TOP`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `linux/const.h`, `asm/mipsregs.h`. Major macro families are `CAC_BASE (2)`, `CKSEG0ADDR_OR (2)`, `CKSEG1ADDR_OR (2)`, `HIGHMEM_START (2)`, `IO_BASE (2)`, `MAP_BASE (2)`, `UNCAC_BASE (2)`, `FIXADDR_TOP (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/topology.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/topology.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/topology.h` defines or delegates NUMA/topology helpers for `mach-generic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 0 macros including none; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm-generic/topology.h`. Major macro families are no major macro families. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is scheduler topology, NUMA node lookup, cpumask helpers, and memory-zone placement.

## Risks
incorrect CPU/node mappings hurt locality or break NUMA memory accounting.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-generic/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ingenic/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ingenic/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ingenic/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ingenic`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 38 macros including `__ASM_MACH_JZ4740_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_vce`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_prefetch`, `cpu_has_mcheck`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `kernel_uses_llsc`, `cpu_has_vtag_icache`, `cpu_has_dc_aliases`, `cpu_has_ic_fills_f_dc`, and 14 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (34)`, `_ (1)`, `cpu_dcache (1)`, `cpu_icache (1)`, `kernel_uses (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ingenic/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip22/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip22/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip22/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ip22`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 30 macros including `__ASM_MACH_IP22_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_4k_cache`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_divec`, `cpu_has_cache_cdex_p`, `cpu_has_prefetch`, `cpu_has_mcheck`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_vtag_icache`, `cpu_has_dc_aliases`, `cpu_has_ic_fills_f_dc`, `cpu_has_dsp`, `cpu_has_dsp2`, `cpu_has_mipsmt`, `cpu_has_userlocal`, `cpu_has_nofpuex`, `cpu_has_64bits`, `cpu_has_mips_2`, and 6 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are `asm/cpu.h`. Major macro families are `cpu_has (29)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip22/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip22/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip22/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip22/spaces.h` overrides virtual/physical address-space constants for `mach-ip22`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `_ASM_MACH_IP22_SPACES_H`, `PHYS_OFFSET`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/spaces.h`. Major macro families are `PHYS_OFFSET (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip22/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 55 macros including `__ASM_MACH_IP27_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_tlbinv`, `cpu_has_segments`, `cpu_has_eva`, `cpu_has_htw`, `cpu_has_rixiex`, `cpu_has_maar`, `cpu_has_rw_llb`, `cpu_has_3kex`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_nofpuex`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_64bits`, `cpu_has_divec`, `cpu_has_vce`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_prefetch`, `cpu_has_mcheck`, and 31 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are `asm/cpu.h`. Major macro families are `cpu_has (50)`, `cpu_icache (2)`, `_ (1)`, `cpu_dcache (1)`, `cpu_scache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 7 macros including `__ASM_MACH_IP27_IRQ_H`, `NR_IRQS`, `IP27_HUB_PEND0_IRQ`, `IP27_HUB_PEND1_IRQ`, `IP27_RT_TIMER_IRQ`, `IP27_HUB_IRQ_BASE`, `IP27_HUB_IRQ_COUNT`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/irq.h`. Major macro families are `IP27_HUB (4)`, `IP27_RT (1)`, `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/kernel-entry-init.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/kernel-entry-init.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/kernel-entry-init.h` supplies machine-specific early-entry assembly hooks for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `__ASM_MACH_IP27_KERNEL_ENTRY_H`, `PAGE_GLOBAL`, `PAGE_VALID`, `PAGE_DIRTY`, `CACHE_CACHABLE_COW`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is assembly macro expansion during kernel entry. The common MIPS entry path invokes these macros before normal C setup, then returns to generic initialization after CP0, cache, TLB, or SMP wait-loop state has been prepared.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/sn/addrs.h`, `asm/sn/agent.h`, `asm/sn/klkernvars.h`. Major macro families are `CACHE_CACHABLE (1)`, `PAGE_DIRTY (1)`, `PAGE_GLOBAL (1)`, `PAGE_VALID (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS reset/vector entry code, CP0 setup, TLB/cache mode selection, SMP secondary entry, and kexec handoff.

## Risks
assembly macros run before normal C runtime services, so register clobbers or CPU-revision checks can break boot very early; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot cold, kexec, and SMP secondary CPUs where supported, because failures can occur before console output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/kernel-entry-init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mangle-port.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mangle-port.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mangle-port.h` customizes I/O port byte-lane/address swizzling for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `__ASM_MACH_IP27_MANGLE_PORT_H`, `__swizzle_addr_b`, `__swizzle_addr_w`, `__swizzle_addr_l`, `__swizzle_addr_q`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (5)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic MIPS port I/O helpers, PCI/ISA-style drivers, bus endian translation, and platform-specific bridge windows.

## Risks
bad swizzle rules silently corrupt byte/word I/O against legacy devices; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mangle-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mmzone.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mmzone.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mmzone.h` defines machine memory-zone and node data hooks for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `_ASM_MACH_MMZONE_H`, `pa_to_nid`, `hub_data`; 4 structs: `hub_data`, `node_data`, `pglist_data`; 0 enums: none; 1 callable helpers/prototypes: `DECLARE_BITMAP`; 1 extern variables: `__node_data`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `DECLARE_BITMAP`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm/sn/addrs.h`, `asm/sn/arch.h`, `asm/sn/agent.h`, `asm/sn/klkernvars.h`. Major macro families are `_ASM (1)`, `hub_data (1)`, `pa_to (1)`. Typed contracts include `hub_data`, `node_data`, `pglist_data`. Callable helpers or declarations include `DECLARE_BITMAP`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is sparsemem, NUMA bootmem setup, pgdat/node data lookup, and platform memory discovery.

## Risks
node-ID and PFN translation mistakes can corrupt memory placement or early page allocator state; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/mmzone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/spaces.h` overrides virtual/physical address-space constants for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 9 macros including `_ASM_MACH_IP27_SPACES_H`, `HSPEC_BASE`, `IO_BASE`, `MSPEC_BASE`, `UNCAC_BASE`, `CAC_BASE`, `TO_MSPEC`, `TO_HSPEC`, `HIGHMEM_START`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `linux/const.h`, `asm/mach-generic/spaces.h`. Major macro families are `CAC_BASE (1)`, `HIGHMEM_START (1)`, `HSPEC_BASE (1)`, `IO_BASE (1)`, `MSPEC_BASE (1)`, `TO_HSPEC (1)`, `TO_MSPEC (1)`, `UNCAC_BASE (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/topology.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/topology.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/topology.h` defines or delegates NUMA/topology helpers for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `_ASM_MACH_TOPOLOGY_H`, `cpu_to_node`, `cpumask_of_node`, `cpumask_of_pcibus`, `node_distance`; 2 structs: `cpuinfo_ip27`, `pci_bus`; 0 enums: none; 1 callable helpers/prototypes: `pcibus_to_node`; 2 extern variables: `sn_cpu_info`, `__node_distances`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `pcibus_to_node`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm/sn/types.h`, `asm/mmzone.h`, `asm-generic/topology.h`. Major macro families are `cpumask_of (2)`, `_ASM (1)`, `cpu_to (1)`, `node_distance (1)`. Typed contracts include `cpuinfo_ip27`, `pci_bus`. Callable helpers or declarations include `pcibus_to_node`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is scheduler topology, NUMA node lookup, cpumask helpers, and memory-zone placement.

## Risks
incorrect CPU/node mappings hurt locality or break NUMA memory accounting; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ip28`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 31 macros including `__ASM_MACH_IP28_CPU_FEATURE_OVERRIDES_H`, `cpu_has_watch`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_divec`, `cpu_has_vce`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_prefetch`, `cpu_has_mcheck`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_vtag_icache`, `cpu_has_dc_aliases`, `cpu_has_ic_fills_f_dc`, `cpu_has_dsp`, `cpu_has_dsp2`, `cpu_icache_snoops_remote_store`, `cpu_has_mipsmt`, `cpu_has_userlocal`, `cpu_has_nofpuex`, `cpu_has_64bits`, `cpu_has_4kex`, `cpu_has_4k_cache`, and 7 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are `asm/cpu.h`. Major macro families are `cpu_has (27)`, `cpu_icache (2)`, `_ (1)`, `cpu_dcache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/spaces.h` overrides virtual/physical address-space constants for `mach-ip28`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `_ASM_MACH_IP28_SPACES_H`, `PHYS_OFFSET`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/spaces.h`. Major macro families are `PHYS_OFFSET (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ip30`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 54 macros including `__ASM_MACH_IP30_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_tlbinv`, `cpu_has_segments`, `cpu_has_eva`, `cpu_has_htw`, `cpu_has_rixiex`, `cpu_has_maar`, `cpu_has_rw_llb`, `cpu_has_3kex`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_nofpuex`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_64bits`, `cpu_has_divec`, `cpu_has_vce`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_prefetch`, `cpu_has_mcheck`, and 30 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are `asm/cpu.h`. Major macro families are `cpu_has (49)`, `cpu_icache (2)`, `_ (1)`, `cpu_dcache (1)`, `cpu_scache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/kernel-entry-init.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/kernel-entry-init.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/kernel-entry-init.h` supplies machine-specific early-entry assembly hooks for `mach-ip30`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__ASM_MACH_IP30_KERNEL_ENTRY_H`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is assembly macro expansion during kernel entry. The common MIPS entry path invokes these macros before normal C setup, then returns to generic initialization after CP0, cache, TLB, or SMP wait-loop state has been prepared.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS reset/vector entry code, CP0 setup, TLB/cache mode selection, SMP secondary entry, and kexec handoff.

## Risks
assembly macros run before normal C runtime services, so register clobbers or CPU-revision checks can break boot very early; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot cold, kexec, and SMP secondary CPUs where supported, because failures can occur before console output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/kernel-entry-init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/mangle-port.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/mangle-port.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/mangle-port.h` customizes I/O port byte-lane/address swizzling for `mach-ip30`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 13 macros including `__ASM_MACH_IP30_MANGLE_PORT_H`, `__swizzle_addr_b`, `__swizzle_addr_w`, `__swizzle_addr_l`, `__swizzle_addr_q`, `ioswabb`, `__mem_ioswabb`, `ioswabw`, `__mem_ioswabw`, `ioswabl`, `__mem_ioswabl`, `ioswabq`, `__mem_ioswabq`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (9)`, `ioswabb (1)`, `ioswabl (1)`, `ioswabq (1)`, `ioswabw (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic MIPS port I/O helpers, PCI/ISA-style drivers, bus endian translation, and platform-specific bridge windows.

## Risks
bad swizzle rules silently corrupt byte/word I/O against legacy devices; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/mangle-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/spaces.h` overrides virtual/physical address-space constants for `mach-ip30`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `_ASM_MACH_IP30_SPACES_H`, `PHYS_OFFSET`, `CAC_BASE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/spaces.h`. Major macro families are `CAC_BASE (1)`, `PHYS_OFFSET (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip30/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ip32`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 24 macros including `__ASM_MACH_IP32_CPU_FEATURE_OVERRIDES_H`, `cpu_has_llsc`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_vce`, `cpu_has_cache_cdex_s`, `cpu_has_mcheck`, `cpu_has_ejtag`, `cpu_has_vtag_icache`, `cpu_has_ic_fills_f_dc`, `cpu_has_dsp`, `cpu_has_dsp2`, `cpu_has_4k_cache`, `cpu_has_mipsmt`, `cpu_has_userlocal`, `cpu_has_mips32r1`, `cpu_has_mips32r2`, `cpu_has_mips64r1`, `cpu_has_mips64r2`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (23)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/kmalloc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/kmalloc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/kmalloc.h` sets machine-specific DMA-safe `kmalloc` alignment for `mach-ip32`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `__ASM_MACH_IP32_KMALLOC_H`, `ARCH_DMA_MINALIGN`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `ARCH_DMA (2)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is SLAB/SLUB allocation, DMA mapping assumptions, cache-line alignment, and platform device drivers.

## Risks
too-small alignment can expose DMA/cache aliasing bugs; too-large alignment wastes memory.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/kmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/mangle-port.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/mangle-port.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/mangle-port.h` customizes I/O port byte-lane/address swizzling for `mach-ip32`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `__ASM_MACH_IP32_MANGLE_PORT_H`, `__swizzle_addr_b`, `__swizzle_addr_w`, `__swizzle_addr_l`, `__swizzle_addr_q`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (5)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic MIPS port I/O helpers, PCI/ISA-style drivers, bus endian translation, and platform-specific bridge windows.

## Risks
bad swizzle rules silently corrupt byte/word I/O against legacy devices.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/mangle-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/floppy.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/floppy.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/floppy.h` implements platform floppy controller I/O, DMA, IRQ, and memory helpers for `mach-jazz`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__ASM_MACH_JAZZ_FLOPPY_H`; 0 structs: none; 0 enums: none; 29 callable helpers/prototypes: `fd_inb`, `fd_outb`, `fd_enable_dma`, `fd_disable_dma`, `fd_request_dma`, `fd_free_dma`, `fd_clear_dma_ff`, `fd_set_dma_mode`, `fd_set_dma_addr`, `fd_set_dma_count`, `fd_get_dma_residue`, `fd_enable_irq`, `fd_disable_irq`, `fd_request_irq`, and 15 more; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `fd_inb`, `fd_outb`, `fd_enable_dma`, `fd_disable_dma`, `fd_request_dma`, `fd_free_dma`, `fd_clear_dma_ff`, `fd_set_dma_mode`, `fd_set_dma_addr`, `fd_set_dma_count`, and 19 more. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/delay.h`, `linux/linkage.h`, `linux/types.h`, `linux/mm.h`, `asm/addrspace.h`, `asm/jazz.h`, `asm/jazzdma.h`. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `fd_inb`, `fd_outb`, `fd_enable_dma`, `fd_disable_dma`, `fd_request_dma`, `fd_free_dma`, `fd_clear_dma_ff`, `fd_set_dma_mode`, `fd_set_dma_addr`, `fd_set_dma_count`, `fd_get_dma_residue`, `fd_enable_irq`, and 17 more. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is legacy floppy block drivers, ISA DMA APIs, platform IRQ allocation, and low-memory DMA buffers.

## Risks
DMA residue/count handling and fixed IRQ/DMA assumptions are fragile on non-PC MIPS systems.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise the specific device path: RTC read/write, floppy DMA/IRQ, timer callbacks, or reset assertion/deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/floppy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/mc146818rtc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/mc146818rtc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/mc146818rtc.h` adapts MC146818-compatible RTC accessors for `mach-jazz`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 4 macros including `__ASM_MACH_JAZZ_MC146818RTC_H`, `RTC_PORT`, `RTC_IRQ`, `RTC_ALWAYS_BCD`; 0 structs: none; 0 enums: none; 3 callable helpers/prototypes: `CMOS_READ`, `CMOS_WRITE`, `outb_p`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `CMOS_READ`, `CMOS_WRITE`, `outb_p`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/delay.h`, `asm/io.h`, `asm/jazz.h`. Major macro families are `RTC_ALWAYS (1)`, `RTC_IRQ (1)`, `RTC_PORT (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `CMOS_READ`, `CMOS_WRITE`, `outb_p`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic RTC/CMOS code, platform I/O mapping, BCD/year handling, and machine time initialization.

## Risks
wrong address, data format, or year handling produces persistent clock drift or invalid wall time.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise the specific device path: RTC read/write, floppy DMA/IRQ, timer callbacks, or reset assertion/deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-jazz/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-lantiq/falcon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 31 macros including `__ASM_MACH_FALCON_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_sb1_cache`, `cpu_has_fpu`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_prefetch`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_mips16`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `cpu_has_mips32r1`, `cpu_has_mips32r2`, `cpu_has_mips64r1`, `cpu_has_mips64r2`, `cpu_has_dsp`, `cpu_has_mipsmt`, and 7 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (28)`, `_ (1)`, `cpu_dcache (1)`, `cpu_icache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/falcon_irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/falcon_irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/falcon_irq.h` defines IRQ number layout and interrupt-controller constants for `mach-lantiq/falcon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 10 macros including `_FALCON_IRQ__`, `INT_NUM_IRQ0`, `INT_NUM_IM0_IRL0`, `INT_NUM_IM1_IRL0`, `INT_NUM_IM2_IRL0`, `INT_NUM_IM3_IRL0`, `INT_NUM_IM4_IRL0`, `INT_NUM_EXTRA_START`, `INT_NUM_IM_OFFSET`, `MAX_IM`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `INT_NUM (8)`, `MAX_IM (1)`, `_FALCON (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/falcon_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-lantiq/falcon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `__FALCON_IRQ_H`, `NR_IRQS`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `falcon_irq.h`, `asm/mach-generic/irq.h`. Major macro families are `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/lantiq_soc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/lantiq_soc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/lantiq_soc.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-lantiq/falcon`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 21 macros including `_LTQ_FALCON_H__`, `SOC_ID_FALCON`, `SOC_TYPE_FALCON`, `LTQ_ASC0_BASE_ADDR`, `LTQ_EARLY_ASC`, `LTQ_RST_CAUSE_WDTRST`, `LTQ_STATUS_BASE_ADDR`, `FALCON_CHIPID`, `FALCON_CHIPTYPE`, `FALCON_CHIPCONF`, `SYSCTL_SYS1`, `SYSCTL_SYSETH`, `SYSCTL_SYSGPE`, `BS_FLASH`, `BS_SPI`, `ltq_ebu_w32`, `ltq_ebu_r32`, `ltq_sys1_w32`, `ltq_sys1_r32`, `ltq_sys1_w32_mask`, `LTQ_EBU_PCC_ISTAT`; 0 structs: none; 0 enums: none; 2 callable helpers/prototypes: `pinctrl_falcon_get_range_size`, `pinctrl_falcon_add_gpio_range`; 2 extern variables: `ltq_ebu_membase`, `ltq_sys1_membase`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `pinctrl_falcon_get_range_size`, `pinctrl_falcon_add_gpio_range`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/pinctrl/pinctrl.h`, `lantiq.h`. Major macro families are `ltq_sys1 (3)`, `ltq_ebu (2)`, `BS_FLASH (1)`, `BS_SPI (1)`, `FALCON_CHIPCONF (1)`, `FALCON_CHIPID (1)`, `FALCON_CHIPTYPE (1)`, `LTQ_ASC0 (1)`. Typed contracts include no structs. Callable helpers or declarations include `pinctrl_falcon_get_range_size`, `pinctrl_falcon_add_gpio_range`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/falcon/lantiq_soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq.h` declares board, firmware, memory, and platform-data contracts for `mach-lantiq`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 13 macros including `_LANTIQ_H__`, `ltq_r32`, `ltq_w32`, `ltq_w32_mask`, `ltq_r8`, `ltq_w8`, `ltq_ebu_w32`, `ltq_ebu_r32`, `ltq_ebu_w32_mask`, `IOPORT_RESOURCE_START`, `IOPORT_RESOURCE_END`, `IOMEM_RESOURCE_START`, `IOMEM_RESOURCE_END`; 0 structs: none; 0 enums: none; 12 callable helpers/prototypes: `ltq_disable_irq`, `ltq_mask_and_ack_irq`, `ltq_enable_irq`, `ltq_eiu_get_irq`, `clk_activate`, `clk_deactivate`, `clk_get_cpu`, `clk_get_fpi`, `clk_get_io`, `clk_get_ppe`, `ltq_boot_select`, `ltq_soc_type`; 2 extern variables: `ltq_ebu_membase`, `ebu_lock`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `ltq_disable_irq`, `ltq_mask_and_ack_irq`, `ltq_enable_irq`, `ltq_eiu_get_irq`, `clk_activate`, `clk_deactivate`, `clk_get_cpu`, `clk_get_fpi`, `clk_get_io`, `clk_get_ppe`, and 2 more. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/irq.h`, `linux/device.h`, `linux/clk.h`. Major macro families are `ltq_ebu (3)`, `IOMEM_RESOURCE (2)`, `IOPORT_RESOURCE (2)`, `ltq_w32 (2)`, `_LANTIQ (1)`, `ltq_r32 (1)`, `ltq_r8 (1)`, `ltq_w8 (1)`. Typed contracts include no structs. Callable helpers or declarations include `ltq_disable_irq`, `ltq_mask_and_ack_irq`, `ltq_enable_irq`, `ltq_eiu_get_irq`, `clk_activate`, `clk_deactivate`, `clk_get_cpu`, `clk_get_fpi`, `clk_get_io`, `clk_get_ppe`, `ltq_boot_select`, `ltq_soc_type`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq_platform.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq_platform.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq_platform.h` declares board, firmware, memory, and platform-data contracts for `mach-lantiq`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `_LANTIQ_PLATFORM_H__`; 2 structs: `ltq_eth_data`, `sockaddr`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `ltq_eth_data`, `sockaddr` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are `linux/socket.h`. Major macro families are `_LANTIQ (1)`. Typed contracts include `ltq_eth_data`, `sockaddr`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-lantiq/xway`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `__LANTIQ_IRQ_H`, `NR_IRQS`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `lantiq_irq.h`, `asm/mach-generic/irq.h`. Major macro families are `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_irq.h` defines IRQ number layout and interrupt-controller constants for `mach-lantiq/xway`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 10 macros including `_LANTIQ_XWAY_IRQ_H__`, `INT_NUM_IRQ0`, `INT_NUM_IM0_IRL0`, `INT_NUM_IM1_IRL0`, `INT_NUM_IM2_IRL0`, `INT_NUM_IM3_IRL0`, `INT_NUM_IM4_IRL0`, `INT_NUM_IM_OFFSET`, `LTQ_DMA_CH0_INT`, `MAX_IM`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `INT_NUM (7)`, `LTQ_DMA (1)`, `MAX_IM (1)`, `_LANTIQ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_soc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_soc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_soc.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-lantiq/xway`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 63 macros including `_LTQ_XWAY_H__`, `SOC_ID_DANUBE1`, `SOC_ID_DANUBE2`, `SOC_ID_TWINPASS`, `SOC_ID_AMAZON_SE_1`, `SOC_ID_AMAZON_SE_2`, `SOC_ID_ARX188`, `SOC_ID_ARX168_1`, `SOC_ID_ARX168_2`, `SOC_ID_ARX182`, `SOC_ID_GRX188`, `SOC_ID_GRX168`, `SOC_ID_VRX288`, `SOC_ID_VRX282`, `SOC_ID_VRX268`, `SOC_ID_GRX268`, `SOC_ID_GRX288`, `SOC_ID_VRX288_2`, `SOC_ID_VRX268_2`, `SOC_ID_GRX288_2`, `SOC_ID_GRX282_2`, `SOC_ID_VRX220`, `SOC_ID_ARX362`, `SOC_ID_ARX368`, and 39 more; 0 structs: none; 0 enums: none; 3 callable helpers/prototypes: `ltq_pmu_enable`, `ltq_pmu_disable`, `ltq_get_cp1_base`; 1 extern variables: `ltq_cgu_membase`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `ltq_pmu_enable`, `ltq_pmu_disable`, `ltq_get_cp1_base`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `lantiq.h`. Major macro families are `SOC_ID (30)`, `SOC_TYPE (9)`, `LTQ_EBU (6)`, `LTQ_MPS (2)`, `ltq_cgu (2)`, `BS_EXT (1)`, `BS_FLASH (1)`, `BS_MII0 (1)`. Typed contracts include no structs. Callable helpers or declarations include `ltq_pmu_enable`, `ltq_pmu_disable`, `ltq_get_cp1_base`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/lantiq_soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/xway_dma.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/xway_dma.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/xway_dma.h` describes low-level controller registers and helper macros for `mach-lantiq/xway`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 10 macros including `LTQ_DMA_H__`, `LTQ_DESC_SIZE`, `LTQ_DESC_NUM`, `LTQ_DMA_OWN`, `LTQ_DMA_C`, `LTQ_DMA_SOP`, `LTQ_DMA_EOP`, `LTQ_DMA_TX_OFFSET`, `LTQ_DMA_RX_OFFSET`, `LTQ_DMA_SIZE_MASK`; 4 structs: `ltq_dma_desc`, `ltq_dma_channel`, `device`; 0 enums: none; 9 callable helpers/prototypes: `ltq_dma_enable_irq`, `ltq_dma_disable_irq`, `ltq_dma_ack_irq`, `ltq_dma_open`, `ltq_dma_close`, `ltq_dma_alloc_tx`, `ltq_dma_alloc_rx`, `ltq_dma_free`, `ltq_dma_init_port`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `ltq_dma_enable_irq`, `ltq_dma_disable_irq`, `ltq_dma_ack_irq`, `ltq_dma_open`, `ltq_dma_close`, `ltq_dma_alloc_tx`, `ltq_dma_alloc_rx`, `ltq_dma_free`, `ltq_dma_init_port`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `LTQ_DMA (8)`, `LTQ_DESC (2)`. Typed contracts include `ltq_dma_desc`, `ltq_dma_channel`, `device`. Callable helpers or declarations include `ltq_dma_enable_irq`, `ltq_dma_disable_irq`, `ltq_dma_ack_irq`, `ltq_dma_open`, `ltq_dma_close`, `ltq_dma_alloc_tx`, `ltq_dma_alloc_rx`, `ltq_dma_free`, `ltq_dma_init_port`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/xway/xway_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-loongson2ef`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 27 macros including `__ASM_MACH_LOONGSON2EF_CPU_FEATURE_OVERRIDES_H`, `cpu_has_32fpr`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_4kex`, `cpu_has_64bits`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_counter`, `cpu_has_dc_aliases`, `cpu_has_divec`, `cpu_has_ejtag`, `cpu_has_inclusive_pcaches`, `cpu_has_llsc`, `cpu_has_mcheck`, `cpu_has_mdmx`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_mips3d`, `cpu_has_mipsmt`, `cpu_has_smartmips`, `cpu_has_tlb`, `cpu_has_vce`, `cpu_has_veic`, and 3 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (26)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536.h` describes low-level controller registers and helper macros for `mach-loongson2ef/cs5536`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 211 macros including `_CS5536_H`, `CS5536_SB_MSR_BASE`, `CS5536_GLIU_MSR_BASE`, `CS5536_ILLEGAL_MSR_BASE`, `CS5536_USB_MSR_BASE`, `CS5536_IDE_MSR_BASE`, `CS5536_DIVIL_MSR_BASE`, `CS5536_ACC_MSR_BASE`, `CS5536_UNUSED_MSR_BASE`, `CS5536_GLCP_MSR_BASE`, `SB_MSR_REG`, `GLIU_MSR_REG`, `ILLEGAL_MSR_REG`, `USB_MSR_REG`, `IDE_MSR_REG`, `DIVIL_MSR_REG`, `ACC_MSR_REG`, `UNUSED_MSR_REG`, `GLCP_MSR_REG`, `CS5536_IRQ_RANGE`, `CS5536_IRQ_LENGTH`, `CS5536_SMB_RANGE`, `CS5536_SMB_LENGTH`, `CS5536_GPIO_RANGE`, and 187 more; 0 structs: none; 0 enums: none; 2 callable helpers/prototypes: `_rdmsr`, `_wrmsr`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `_rdmsr`, `_wrmsr`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`. Major macro families are `GLIU_IOD (18)`, `SOFT_BAR (10)`, `DIVIL_LBAR (7)`, `GLIU_P2D (7)`, `PIC_YSEL (5)`, `GLCP_CLK (4)`, `PCI_MSR (4)`, `CS5536_ACC (3)`. Typed contracts include no structs. Callable helpers or declarations include `_rdmsr`, `_wrmsr`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; the file contains 211 macros, so broad edits have high review cost and should be grouped by register block or bit-field family; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_mfgpt.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_mfgpt.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_mfgpt.h` describes low-level controller registers and helper macros for `mach-loongson2ef/cs5536`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 7 macros including `_CS5536_MFGPT_H`, `MFGPT_TICK_RATE`, `COMPARE`, `MFGPT_BASE`, `MFGPT0_CMP2`, `MFGPT0_CNT`, `MFGPT0_SETUP`; 0 structs: none; 0 enums: none; 3 callable helpers/prototypes: `setup_mfgpt0_timer`, `disable_mfgpt0_counter`, `enable_mfgpt0_counter`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `setup_mfgpt0_timer`, `disable_mfgpt0_counter`, `enable_mfgpt0_counter`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `cs5536/cs5536.h`, `cs5536/cs5536_pci.h`. Major macro families are `COMPARE (1)`, `MFGPT0_CMP2 (1)`, `MFGPT0_CNT (1)`, `MFGPT0_SETUP (1)`, `MFGPT_BASE (1)`, `MFGPT_TICK (1)`, `_CS5536 (1)`. Typed contracts include no structs. Callable helpers or declarations include `setup_mfgpt0_timer`, `disable_mfgpt0_counter`, `enable_mfgpt0_counter`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_mfgpt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_pci.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_pci.h` describes low-level controller registers and helper macros for `mach-loongson2ef/cs5536`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 64 macros including `_CS5536_PCI_H`, `CS5536_ACC_INTR`, `CS5536_IDE_INTR`, `CS5536_USB_INTR`, `CS5536_MFGPT_INTR`, `CS5536_UART1_INTR`, `CS5536_UART2_INTR`, `PCI_BUS_CS5536`, `PCI_IDSEL_CS5536`, `CFG_PCI_VENDOR_ID`, `CS5536_VENDOR_ID`, `CS5536_ISA_DEVICE_ID`, `CS5536_IDE_DEVICE_ID`, `CS5536_ACC_DEVICE_ID`, `CS5536_OHCI_DEVICE_ID`, `CS5536_EHCI_DEVICE_ID`, `CS5536_ISA_CLASS_CODE`, `CS5536_IDE_CLASS_CODE`, `CS5536_ACC_CLASS_CODE`, `CS5536_OHCI_CLASS_CODE`, `CS5536_EHCI_CLASS_CODE`, `CFG_PCI_CACHE_LINE_SIZE`, `PCI_NONE_BIST`, `PCI_BRIDGE_HEADER_TYPE`, and 40 more; 0 structs: none; 0 enums: none; 15 callable helpers/prototypes: `cs5536_pci_conf_write4`, `cs5536_pci_conf_read4`, `pci_ehci_write_reg`, `pci_ehci_read_reg`, `pci_ide_write_reg`, `pci_ide_read_reg`, `pci_acc_write_reg`, `pci_acc_read_reg`, `pci_ohci_write_reg`, `pci_ohci_read_reg`, `pci_isa_write_bar`, `pci_isa_read_bar`, `pci_isa_write_reg`, `pci_isa_read_reg`, and 1 more; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `cs5536_pci_conf_write4`, `cs5536_pci_conf_read4`, `pci_ehci_write_reg`, `pci_ehci_read_reg`, `pci_ide_write_reg`, `pci_ide_read_reg`, `pci_acc_write_reg`, `pci_acc_read_reg`, `pci_ohci_write_reg`, `pci_ohci_read_reg`, and 5 more. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/init.h`, `linux/types.h`, `linux/pci_regs.h`. Major macro families are `PCI_IDE (6)`, `CS5536_IDE (5)`, `CS5536_ACC (4)`, `CFG_PCI (3)`, `CS5536_EHCI (3)`, `CS5536_ISA (3)`, `CS5536_OHCI (3)`, `PCI_EHCI (3)`. Typed contracts include no structs. Callable helpers or declarations include `cs5536_pci_conf_write4`, `cs5536_pci_conf_read4`, `pci_ehci_write_reg`, `pci_ehci_read_reg`, `pci_ide_write_reg`, `pci_ide_read_reg`, `pci_acc_write_reg`, `pci_acc_read_reg`, `pci_ohci_write_reg`, `pci_ohci_read_reg`, `pci_isa_write_bar`, `pci_isa_read_bar`, and 3 more. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_vsm.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_vsm.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_vsm.h` describes low-level controller registers and helper macros for `mach-loongson2ef/cs5536`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `_CS5536_VSM_H`, `DECLARE_CS5536_MODULE`; 0 structs: none; 0 enums: none; 1 callable helpers/prototypes: `_read_reg`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `_read_reg`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`. Major macro families are `DECLARE_CS5536 (1)`, `_CS5536 (1)`. Typed contracts include no structs. Callable helpers or declarations include `_read_reg`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_vsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/loongson.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/loongson.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/loongson.h` declares board, firmware, memory, and platform-data contracts for `mach-loongson2ef`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 167 macros including `__ASM_MACH_LOONGSON2EF_LOONGSON_H`, `delay`, `LOONGSON_REG`, `LOONGSON_IRQ_BASE`, `LOONGSON_FLASH_BASE`, `LOONGSON_FLASH_SIZE`, `LOONGSON_FLASH_TOP`, `LOONGSON_LIO0_BASE`, `LOONGSON_LIO0_SIZE`, `LOONGSON_LIO0_TOP`, `LOONGSON_BOOT_BASE`, `LOONGSON_BOOT_SIZE`, `LOONGSON_BOOT_TOP`, `LOONGSON_REG_BASE`, `LOONGSON_REG_SIZE`, `LOONGSON_REG_TOP`, `LOONGSON_LIO1_BASE`, `LOONGSON_LIO1_SIZE`, `LOONGSON_LIO1_TOP`, `LOONGSON_PCILO0_BASE`, `LOONGSON_PCILO1_BASE`, `LOONGSON_PCILO2_BASE`, `LOONGSON_PCILO_BASE`, `LOONGSON_PCILO_SIZE`, and 143 more; 0 structs: none; 0 enums: none; 19 callable helpers/prototypes: `prom_init_uart_base`, `loongson2ef_pcibios_init`, `bonito_irq_init`, `mach_prepare_reboot`, `mach_prepare_shutdown`, `mach_prom_init_machtype`, `prom_init_memory`, `prom_init_machtype`, `prom_init_env`, `prom_init_loongson_uart_base`, `bonito_irqdispatch`, `mach_init_irq`, `mach_irq_dispatch`, `mach_i8259_irq`, and 5 more; 3 extern variables: `cpu_clock_freq`, `loongson2_clockmod_table`, `_loongson_addrwincfg_base`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `prom_init_uart_base`, `loongson2ef_pcibios_init`, `bonito_irq_init`, `mach_prepare_reboot`, `mach_prepare_shutdown`, `mach_prom_init_machtype`, `prom_init_memory`, `prom_init_machtype`, `prom_init_env`, `prom_init_loongson_uart_base`, and 9 more. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/io.h`, `linux/init.h`, `linux/irq.h`, `linux/cpufreq.h`. Major macro families are `LOONGSON_GENCFG (20)`, `LOONGSON_ICU (19)`, `LOONGSON_PCICMD (10)`, `LOONGSON_PCIMAP (10)`, `LOONGSON_PCI (8)`, `LOONGSON_ADDRWIN (4)`, `LOONGSON_MEM (4)`, `LOONGSON_REG (4)`. Typed contracts include no structs. Callable helpers or declarations include `prom_init_uart_base`, `loongson2ef_pcibios_init`, `bonito_irq_init`, `mach_prepare_reboot`, `mach_prepare_shutdown`, `mach_prom_init_machtype`, `prom_init_memory`, `prom_init_machtype`, `prom_init_env`, `prom_init_loongson_uart_base`, `bonito_irqdispatch`, `mach_init_irq`, and 7 more. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; the file contains 167 macros, so broad edits have high review cost and should be grouped by register block or bit-field family; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/loongson.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/machine.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/machine.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/machine.h` declares board, firmware, memory, and platform-data contracts for `mach-loongson2ef`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `__ASM_MACH_LOONGSON2EF_MACHINE_H`, `LOONGSON_MACHTYPE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `LOONGSON_MACHTYPE (2)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/mem.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/mem.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/mem.h` declares board, firmware, memory, and platform-data contracts for `mach-loongson2ef`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 6 macros including `__ASM_MACH_LOONGSON2EF_MEM_H`, `LOONGSON_HIGHMEM_START`, `LOONGSON_MMIO_MEM_START`, `LOONGSON_MMIO_MEM_END`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `LOONGSON_MMIO (3)`, `LOONGSON_HIGHMEM (2)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/pci.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/pci.h` describes low-level controller registers and helper macros for `mach-loongson2ef`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 10 macros including `__ASM_MACH_LOONGSON2EF_PCI_H_`, `LOONGSON_PCI_IO_START`, `LOONGSON_CPU_MEM_SRC`, `LOONGSON_PCI_MEM_DST`, `LOONGSON_PCI_MEM_START`, `LOONGSON_PCI_MEM_END`, `MMAP_CPUTOPCI_SIZE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 1 extern variables: `loongson_pci_ops`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `LOONGSON_PCI (7)`, `LOONGSON_CPU (1)`, `MMAP_CPUTOPCI (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/spaces.h` overrides virtual/physical address-space constants for `mach-loongson2ef`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `__ASM_MACH_LOONGSON2EF_SPACES_H_`, `CAC_BASE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/spaces.h`. Major macro families are `CAC_BASE (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/boot_param.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/boot_param.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/boot_param.h` declares board, firmware, memory, and platform-data contracts for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 22 macros including `__ASM_MACH_LOONGSON64_BOOT_PARAM_H_`, `SYSTEM_RAM_LOW`, `SYSTEM_RAM_HIGH`, `SYSTEM_RAM_RESERVED`, `PCI_IO`, `PCI_MEM`, `LOONGSON_CFG_REG`, `VIDEO_ROM`, `ADAPTER_ROM`, `ACPI_TABLE`, `SMBIOS_TABLE`, `UMA_VIDEO_RAM`, `VUMA_VIDEO_RAM`, `MAX_MEMORY_TYPE`, `MEM_SIZE_IS_IN_BYTES`, `LOONGSON3_BOOT_MEM_MAP_MAX`, `MAX_UARTS`, `MAX_SENSORS`, `SENSOR_TEMPER`, `SENSOR_VOLTAGE`, `SENSOR_FAN`, `MAX_RESOURCE_NUMBER`; 26 structs: `efi_memory_map_loongson`, `mem_map`, `efi_cpuinfo_loongson`, `uart_device`, `sensor_device`, `system_loongson`, `irq_source_routing_table`, `interface_info`, `resource_loongson`, `archdev_data`, `board_devices`, `loongson_special_attribute`, `loongson_params`, `smbios_tables`, and 3 more; 2 enums: `loongson_cpu_type`, `loongson_bridge_type`; 3 callable helpers/prototypes: `ls7a_early_config`, `rs780e_early_config`, `virtual_early_config`; 6 extern variables: `loongson_memmap`, `loongson_sysconf`, `eboard`, `einter`, `especial`, `node_id_offset`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `ls7a_early_config`, `rs780e_early_config`, `virtual_early_config`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`. Major macro families are `SYSTEM_RAM (3)`, `ACPI_TABLE (1)`, `ADAPTER_ROM (1)`, `LOONGSON3_BOOT (1)`, `LOONGSON_CFG (1)`, `MAX_MEMORY (1)`, `MAX_RESOURCE (1)`, `MAX_SENSORS (1)`. Typed contracts include `efi_memory_map_loongson`, `mem_map`, `efi_cpuinfo_loongson`, `uart_device`, `sensor_device`, `system_loongson`, `irq_source_routing_table`, `interface_info`, `resource_loongson`, `archdev_data`, and 7 more. Callable helpers or declarations include `ls7a_early_config`, `rs780e_early_config`, `virtual_early_config`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/boot_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/builtin_dtbs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/builtin_dtbs.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/builtin_dtbs.h` provides machine-specific constants and declarations for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__ASM_MACH_LOONGSON64_BUILTIN_DTBS_H_`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 6 extern variables: `__dtb_loongson64_2core_2k1000_begin`, `__dtb_loongson64c_4core_ls7a_begin`, `__dtb_loongson64c_4core_rs780e_begin`, `__dtb_loongson64c_8core_rs780e_begin`, `__dtb_loongson64g_4core_ls7a_begin`, `__dtb_loongson64v_4core_virtio_begin`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/builtin_dtbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 31 macros including `__ASM_MACH_LOONGSON64_CPU_FEATURE_OVERRIDES_H`, `cpu_has_32fpr`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_4kex`, `cpu_has_64bits`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_counter`, `cpu_has_dc_aliases`, `cpu_has_divec`, `cpu_has_inclusive_pcaches`, `cpu_has_llsc`, `cpu_has_mcheck`, `cpu_has_mdmx`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_mips3d`, `cpu_has_mipsmt`, `cpu_has_smartmips`, `cpu_has_tlb`, `cpu_has_vce`, `cpu_has_veic`, `cpu_has_vint`, and 7 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (29)`, `_ (1)`, `cpu_hwrena (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpucfg-emul.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpucfg-emul.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpucfg-emul.h` provides machine-specific constants and declarations for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `_ASM_MACH_LOONGSON64_CPUCFG_EMUL_H_`, `LOONGSON_FPREV_MASK`; 0 structs: none; 0 enums: none; 3 callable helpers/prototypes: `loongson3_cpucfg_emulation_enabled`, `loongson3_cpucfg_read_synthesized`, `loongson3_cpucfg_synthesize_data`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `loongson3_cpucfg_emulation_enabled`, `loongson3_cpucfg_read_synthesized`, `loongson3_cpucfg_synthesize_data`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm/cpu-info.h`, `loongson_regs.h`. Major macro families are `LOONGSON_FPREV (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include `loongson3_cpucfg_emulation_enabled`, `loongson3_cpucfg_read_synthesized`, `loongson3_cpucfg_synthesize_data`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpucfg-emul.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 8 macros including `__ASM_MACH_LOONGSON64_IRQ_H_`, `NR_IRQS_LEGACY`, `NR_MIPS_CPU_IRQS`, `NR_MAX_CHAINED_IRQS`, `NR_IRQS`, `MAX_IO_PICS`, `MIPS_CPU_IRQ_BASE`, `GSI_MIN_CPU_IRQ`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/irq.h`. Major macro families are `NR_IRQS (2)`, `GSI_MIN (1)`, `MAX_IO (1)`, `MIPS_CPU (1)`, `NR_MAX (1)`, `NR_MIPS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/kernel-entry-init.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/kernel-entry-init.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/kernel-entry-init.h` supplies machine-specific early-entry assembly hooks for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `__ASM_MACH_LOONGSON64_KERNEL_ENTRY_H`, `USE_KEXEC_SMP_WAIT_FINAL`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is assembly macro expansion during kernel entry. The common MIPS entry path invokes these macros before normal C setup, then returns to generic initialization after CP0, cache, TLB, or SMP wait-loop state has been prepared.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/cpu.h`. Major macro families are `USE_KEXEC (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS reset/vector entry code, CP0 setup, TLB/cache mode selection, SMP secondary entry, and kexec handoff.

## Risks
assembly macros run before normal C runtime services, so register clobbers or CPU-revision checks can break boot very early; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot cold, kexec, and SMP secondary CPUs where supported, because failures can occur before console output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/kernel-entry-init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson.h` declares board, firmware, memory, and platform-data contracts for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 136 macros including `__ASM_MACH_LOONGSON64_LOONGSON_H`, `delay`, `LOONGSON_REG`, `LOONGSON3_REG8`, `LOONGSON3_REG32`, `LOONGSON_FLASH_BASE`, `LOONGSON_FLASH_SIZE`, `LOONGSON_FLASH_TOP`, `LOONGSON_LIO0_BASE`, `LOONGSON_LIO0_SIZE`, `LOONGSON_LIO0_TOP`, `LOONGSON_BOOT_BASE`, `LOONGSON_BOOT_SIZE`, `LOONGSON_BOOT_TOP`, `LOONGSON_REG_BASE`, `LOONGSON_REG_SIZE`, `LOONGSON_REG_TOP`, `LOONGSON3_REG_BASE`, `LOONGSON3_REG_SIZE`, `LOONGSON3_REG_TOP`, `LOONGSON_LIO1_BASE`, `LOONGSON_LIO1_SIZE`, `LOONGSON_LIO1_TOP`, `LOONGSON_PCILO0_BASE`, and 112 more; 1 structs: `loongson_system_configuration`; 4 enums: `loongson_fw_interface`, `loongson_cpu_type`, `loongson_bridge_type`; 8 callable helpers/prototypes: `void`, `mach_prepare_reboot`, `mach_prepare_shutdown`, `prom_dtb_init_env`, `prom_lefi_init_env`, `szmem`, `mach_irq_dispatch`, `mach_i8259_irq`; 6 extern variables: `cpu_clock_freq`, `loongson3_smp_ops`, `loongson_fdt_blob`, `loongson_chipcfg`, `loongson_chiptemp`, `loongson_freqctrl`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `void`, `mach_prepare_reboot`, `mach_prepare_shutdown`, `prom_dtb_init_env`, `prom_lefi_init_env`, `szmem`, `mach_irq_dispatch`, `mach_i8259_irq`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/io.h`, `linux/init.h`, `linux/irq.h`, `boot_param.h`. Major macro families are `LOONGSON_GENCFG (20)`, `LOONGSON_ICU (19)`, `LOONGSON_PCICMD (10)`, `LOONGSON_PCIMAP (10)`, `LOONGSON_PCI (8)`, `LOONGSON_MEM (4)`, `LOONGSON_REG (4)`, `LOONGSON3_REG (3)`. Typed contracts include `loongson_system_configuration`. Callable helpers or declarations include `void`, `mach_prepare_reboot`, `mach_prepare_shutdown`, `prom_dtb_init_env`, `prom_lefi_init_env`, `szmem`, `mach_irq_dispatch`, `mach_i8259_irq`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; the file contains 136 macros, so broad edits have high review cost and should be grouped by register block or bit-field family; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_hwmon.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_hwmon.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_hwmon.h` provides machine-specific constants and declarations for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 9 macros including `__LOONGSON_HWMON_H_`, `MIN_TEMP`, `MAX_TEMP`, `NOT_VALID_TEMP`, `CONSTANT_SPEED_POLICY`, `STEP_SPEED_POLICY`, `KERNEL_HELPER_POLICY`, `MAX_STEP_NUM`, `MAX_FAN_LEVEL`; 5 structs: `temp_range`, `loongson_fan_policy`, `delayed_work`; 1 enums: `fan_control_mode`; 1 callable helpers/prototypes: `loongson3_cpu_temp`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `loongson3_cpu_temp`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`. Major macro families are `CONSTANT_SPEED (1)`, `KERNEL_HELPER (1)`, `MAX_FAN (1)`, `MAX_STEP (1)`, `MAX_TEMP (1)`, `MIN_TEMP (1)`, `NOT_VALID (1)`, `STEP_SPEED (1)`. Typed contracts include `temp_range`, `loongson_fan_policy`, `delayed_work`. Callable helpers or declarations include `loongson3_cpu_temp`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_hwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_regs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_regs.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_regs.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 116 macros including `_LOONGSON_REGS_H_`, `LOONGSON_CFG0`, `LOONGSON_CFG0_PRID`, `LOONGSON_CFG1`, `LOONGSON_CFG1_FP`, `LOONGSON_CFG1_FPREV`, `LOONGSON_CFG1_MMI`, `LOONGSON_CFG1_MSA1`, `LOONGSON_CFG1_MSA2`, `LOONGSON_CFG1_CGP`, `LOONGSON_CFG1_WRP`, `LOONGSON_CFG1_LSX1`, `LOONGSON_CFG1_LSX2`, `LOONGSON_CFG1_LASX`, `LOONGSON_CFG1_R6FXP`, `LOONGSON_CFG1_R6CRCP`, `LOONGSON_CFG1_R6FPP`, `LOONGSON_CFG1_CNT64`, `LOONGSON_CFG1_LSLDR0`, `LOONGSON_CFG1_LSPREF`, `LOONGSON_CFG1_LSPREFX`, `LOONGSON_CFG1_LSSYNCI`, `LOONGSON_CFG1_LSUCA`, `LOONGSON_CFG1_LLSYNC`, and 92 more; 0 structs: none; 0 enums: none; 8 callable helpers/prototypes: `cpu_has_cfg`, `read_cpucfg`, `cpu_has_csr`, `csr_readl`, `csr_readq`, `csr_writel`, `csr_writeq`, `drdtime`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `cpu_has_cfg`, `read_cpucfg`, `cpu_has_csr`, `csr_readl`, `csr_readq`, `csr_writel`, `csr_writeq`, `drdtime`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`, `linux/bits.h`, `asm/mipsregs.h`, `asm/cpu.h`. Major macro families are `LOONGSON_CFG1 (31)`, `LOONGSON_CFG2 (28)`, `LOONGSON_CFG3 (15)`, `LOONGSON_CSR (12)`, `CSR_MAIL (7)`, `LOONGSON_CSRF (6)`, `CSR_IPI (3)`, `LOONGSON_CFG5 (3)`. Typed contracts include no structs. Callable helpers or declarations include `cpu_has_cfg`, `read_cpucfg`, `cpu_has_csr`, `csr_readl`, `csr_readq`, `csr_writel`, `csr_writeq`, `drdtime`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral; the file contains 116 macros, so broad edits have high review cost and should be grouped by register block or bit-field family; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/loongson_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/mmzone.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/mmzone.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/mmzone.h` defines machine memory-zone and node data hooks for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 4 macros including `_ASM_MACH_LOONGSON64_MMZONE_H`, `NODE_ADDRSPACE_SHIFT`, `pa_to_nid`, `nid_to_addrbase`; 0 structs: none; 0 enums: none; 1 callable helpers/prototypes: `prom_init_numa_memory`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `prom_init_numa_memory`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `NODE_ADDRSPACE (1)`, `_ASM (1)`, `nid_to (1)`, `pa_to (1)`. Typed contracts include no structs. Callable helpers or declarations include `prom_init_numa_memory`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is sparsemem, NUMA bootmem setup, pgdat/node data lookup, and platform memory discovery.

## Risks
node-ID and PFN translation mistakes can corrupt memory placement or early page allocator state; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/mmzone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/pci.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/pci.h` describes low-level controller registers and helper macros for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 4 macros including `__ASM_MACH_LOONGSON64_PCI_H_`, `LOONGSON_PCI_IO_START`, `LOONGSON_PCI_MEM_START`, `LOONGSON_PCI_MEM_END`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 1 extern variables: `loongson_pci_ops`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `LOONGSON_PCI (3)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/spaces.h` overrides virtual/physical address-space constants for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 7 macros including `__ASM_MACH_LOONGSON64_SPACES_H_`, `CAC_BASE`, `PCI_PORT_BASE`, `PCI_IOBASE`, `PCI_IOSIZE`, `MAP_BASE`, `IO_SPACE_LIMIT`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/spaces.h`. Major macro families are `CAC_BASE (1)`, `IO_SPACE (1)`, `MAP_BASE (1)`, `PCI_IOBASE (1)`, `PCI_IOSIZE (1)`, `PCI_PORT (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/topology.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/topology.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/topology.h` defines or delegates NUMA/topology helpers for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `_ASM_MACH_TOPOLOGY_H`, `cpu_to_node`, `cpumask_of_node`, `cpumask_of_pcibus`, `node_distance`; 1 structs: `pci_bus`; 0 enums: none; 1 callable helpers/prototypes: `pcibus_to_node`; 2 extern variables: `__node_cpumask`, `__node_distances`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `pcibus_to_node`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm-generic/topology.h`. Major macro families are `cpumask_of (2)`, `_ASM (1)`, `cpu_to (1)`, `node_distance (1)`. Typed contracts include `pci_bus`. Callable helpers or declarations include `pcibus_to_node`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is scheduler topology, NUMA node lookup, cpumask helpers, and memory-zone placement.

## Risks
incorrect CPU/node mappings hurt locality or break NUMA memory accounting; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/workarounds.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/workarounds.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/workarounds.h` provides machine-specific constants and declarations for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `__ASM_MACH_LOONGSON64_WORKAROUNDS_H_`, `WORKAROUND_CPUFREQ`, `WORKAROUND_CPUHOTPLUG`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `WORKAROUND_CPUFREQ (1)`, `WORKAROUND_CPUHOTPLUG (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/workarounds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-malta`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 23 macros including `__ASM_MACH_MIPS_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_4k_cache`, `cpu_has_counter`, `cpu_has_divec`, `cpu_has_vce`, `cpu_has_mcheck`, `cpu_has_llsc`, `cpu_has_clo_clz`, `cpu_has_nofpuex`, `cpu_icache_snoops_remote_store`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (20)`, `cpu_icache (2)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-malta`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `__ASM_MACH_MIPS_IRQ_H`, `NR_IRQS`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/irq.h`. Major macro families are `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/kernel-entry-init.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/kernel-entry-init.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/kernel-entry-init.h` supplies machine-specific early-entry assembly hooks for `mach-malta`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__ASM_MACH_MIPS_KERNEL_ENTRY_INIT_H`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is assembly macro expansion during kernel entry. The common MIPS entry path invokes these macros before normal C setup, then returns to generic initialization after CP0, cache, TLB, or SMP wait-loop state has been prepared.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/regdef.h`, `asm/mipsregs.h`. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS reset/vector entry code, CP0 setup, TLB/cache mode selection, SMP secondary entry, and kexec handoff.

## Risks
assembly macros run before normal C runtime services, so register clobbers or CPU-revision checks can break boot very early.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot cold, kexec, and SMP secondary CPUs where supported, because failures can occur before console output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/kernel-entry-init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/mach-gt64120.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/mach-gt64120.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/mach-gt64120.h` provides machine-specific constants and declarations for `mach-malta`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `_ASM_MACH_MIPS_MACH_GT64120_DEP_H`, `MIPS_GT_BASE`, `GT64120_BASE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 1 extern variables: `_pcictrl_gt64120`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `GT64120_BASE (1)`, `MIPS_GT (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/mach-gt64120.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/mc146818rtc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/mc146818rtc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/mc146818rtc.h` adapts MC146818-compatible RTC accessors for `mach-malta`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 4 macros including `__ASM_MACH_MALTA_MC146818RTC_H`, `RTC_PORT`, `RTC_IRQ`, `RTC_ALWAYS_BCD`; 0 structs: none; 0 enums: none; 3 callable helpers/prototypes: `CMOS_READ`, `CMOS_WRITE`, `outb`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `CMOS_READ`, `CMOS_WRITE`, `outb`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm/io.h`, `asm/mips-boards/generic.h`, `asm/mips-boards/malta.h`. Major macro families are `RTC_ALWAYS (1)`, `RTC_IRQ (1)`, `RTC_PORT (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include `CMOS_READ`, `CMOS_WRITE`, `outb`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic RTC/CMOS code, platform I/O mapping, BCD/year handling, and machine time initialization.

## Risks
wrong address, data format, or year handling produces persistent clock drift or invalid wall time.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise the specific device path: RTC read/write, floppy DMA/IRQ, timer callbacks, or reset assertion/deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/spaces.h` overrides virtual/physical address-space constants for `mach-malta`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `_ASM_MALTA_SPACES_H`, `PAGE_OFFSET`, `PHYS_OFFSET`, `HIGHMEM_START`, `__pa_symbol`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/spaces.h`. Major macro families are `HIGHMEM_START (1)`, `PAGE_OFFSET (1)`, `PHYS_OFFSET (1)`, `_ (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-malta/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-n64/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-n64/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-n64/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-n64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `__ASM_MACH_N64_IRQ_H`, `NR_IRQS`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/irq.h`. Major macro families are `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-n64/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-n64/kmalloc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-n64/kmalloc.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-n64/kmalloc.h` sets machine-specific DMA-safe `kmalloc` alignment for `mach-n64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `__ASM_MACH_N64_KMALLOC_H`, `ARCH_DMA_MINALIGN`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `ARCH_DMA (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is SLAB/SLUB allocation, DMA mapping assumptions, cache-line alignment, and platform device drivers.

## Risks
too-small alignment can expose DMA/cache aliasing bugs; too-large alignment wastes memory.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-n64/kmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-pic32`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 11 macros including `__ASM_MACH_PIC32_CPU_FEATURE_OVERRIDES_H`, `cpu_has_vint`, `cpu_has_veic`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_4k_cache`, `cpu_has_fpu`, `cpu_has_counter`, `cpu_has_llsc`, `cpu_has_nofpuex`, `cpu_icache_snoops_remote_store`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (9)`, `_ (1)`, `cpu_icache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-pic32`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `__ASM_MACH_PIC32_IRQ_H`, `NR_IRQS`, `MIPS_CPU_IRQ_BASE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/irq.h`. Major macro families are `MIPS_CPU (1)`, `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/spaces.h` overrides virtual/physical address-space constants for `mach-pic32`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `_ASM_MACH_PIC32_SPACES_H`, `PHYS_OFFSET`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/spaces.h`. Major macro families are `PHYS_OFFSET (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-pic32/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-ralink`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 3 macros including `__ASM_MACH_RALINK_IRQ_H`, `GIC_NUM_INTRS`, `NR_IRQS`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/irq.h`. Major macro families are `GIC_NUM (1)`, `NR_IRQS (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7620.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7620.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7620.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-ralink`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 32 macros including `_MT7620_REGS_H_`, `IOMEM`, `MT7620_SYSC_BASE`, `SYSC_REG_CHIP_NAME0`, `SYSC_REG_CHIP_NAME1`, `SYSC_REG_EFUSE_CFG`, `SYSC_REG_CHIP_REV`, `SYSC_REG_SYSTEM_CONFIG0`, `SYSC_REG_SYSTEM_CONFIG1`, `MT7620_CHIP_NAME0`, `MT7620_CHIP_NAME1`, `MT7628_CHIP_NAME1`, `CHIP_REV_PKG_MASK`, `CHIP_REV_PKG_SHIFT`, `CHIP_REV_VER_MASK`, `CHIP_REV_VER_SHIFT`, `CHIP_REV_ECO_MASK`, `SYSCFG0_DRAM_TYPE_MASK`, `SYSCFG0_DRAM_TYPE_SHIFT`, `SYSCFG0_DRAM_TYPE_SDRAM`, `SYSCFG0_DRAM_TYPE_DDR1`, `SYSCFG0_DRAM_TYPE_DDR2`, `SYSCFG0_DRAM_TYPE_UNKNOWN`, `SYSCFG0_DRAM_TYPE_DDR2_MT7628`, and 8 more; 0 structs: none; 0 enums: none; 2 callable helpers/prototypes: `is_mt76x8`, `mt7620_get_eco`; 1 extern variables: `ralink_soc`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `is_mt76x8`, `mt7620_get_eco`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `SYSCFG0_DRAM (8)`, `SYSC_REG (6)`, `CHIP_REV (5)`, `MT7620_CHIP (2)`, `MT7620_DDR1 (2)`, `MT7620_DDR2 (2)`, `MT7620_SDRAM (2)`, `IOMEM (1)`. Typed contracts include no structs. Callable helpers or declarations include `is_mt76x8`, `mt7620_get_eco`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7620.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7620/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7620/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7620/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ralink/mt7620`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 30 macros including `_MT7620_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_sb1_cache`, `cpu_has_fpu`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_prefetch`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_mips16`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `cpu_has_mips32r1`, `cpu_has_mips32r2`, `cpu_has_mips64r1`, `cpu_has_mips64r2`, `cpu_has_dsp`, `cpu_has_dsp2`, and 6 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (27)`, `_MT7620 (1)`, `cpu_dcache (1)`, `cpu_icache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7620/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7621.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7621.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7621.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-ralink`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 21 macros including `_MT7621_REGS_H_`, `IOMEM`, `MT7621_PALMBUS_BASE`, `MT7621_PALMBUS_SIZE`, `MT7621_SYSC_BASE`, `SYSC_REG_CHIP_NAME0`, `SYSC_REG_CHIP_NAME1`, `SYSC_REG_CHIP_REV`, `SYSC_REG_SYSTEM_CONFIG0`, `SYSC_REG_SYSTEM_CONFIG1`, `CHIP_REV_PKG_MASK`, `CHIP_REV_PKG_SHIFT`, `CHIP_REV_VER_MASK`, `CHIP_REV_VER_SHIFT`, `CHIP_REV_ECO_MASK`, `MT7621_LOWMEM_BASE`, `MT7621_LOWMEM_MAX_SIZE`, `MT7621_HIGHMEM_BASE`, `MT7621_HIGHMEM_SIZE`, `MT7621_CHIP_NAME0`, `MT7621_CHIP_NAME1`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `CHIP_REV (5)`, `SYSC_REG (5)`, `MT7621_CHIP (2)`, `MT7621_HIGHMEM (2)`, `MT7621_LOWMEM (2)`, `MT7621_PALMBUS (2)`, `IOMEM (1)`, `MT7621_SYSC (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7621.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7621/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7621/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7621/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ralink/mt7621`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 35 macros including `_MT7621_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_sb1_cache`, `cpu_has_fpu`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_prefetch`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_mips16`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `cpu_has_mips32r1`, `cpu_has_mips32r2`, `cpu_has_mips64r1`, `cpu_has_mips64r2`, `cpu_has_dsp`, `cpu_has_dsp2`, and 11 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (32)`, `_MT7621 (1)`, `cpu_dcache (1)`, `cpu_icache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/mt7621/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/ralink_regs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/ralink_regs.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/ralink_regs.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-ralink`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `_RALINK_REGS_H_`; 0 structs: none; 1 enums: `ralink_soc_type`; 6 callable helpers/prototypes: `rt_sysc_w32`, `rt_sysc_r32`, `rt_sysc_m32`, `rt_memc_w32`, `rt_memc_r32`, `__raw_writel`; 3 extern variables: `ralink_soc`, `rt_sysc_membase`, `rt_memc_membase`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `rt_sysc_w32`, `rt_sysc_r32`, `rt_sysc_m32`, `rt_memc_w32`, `rt_memc_r32`, `__raw_writel`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/io.h`. Major macro families are `_RALINK (1)`. Typed contracts include no structs. Callable helpers or declarations include `rt_sysc_w32`, `rt_sysc_r32`, `rt_sysc_m32`, `rt_memc_w32`, `rt_memc_r32`, `__raw_writel`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/ralink_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt288x.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt288x.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt288x.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-ralink`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 15 macros including `_RT288X_REGS_H_`, `IOMEM`, `RT2880_SYSC_BASE`, `SYSC_REG_CHIP_NAME0`, `SYSC_REG_CHIP_NAME1`, `SYSC_REG_CHIP_ID`, `SYSC_REG_SYSTEM_CONFIG`, `RT2880_CHIP_NAME0`, `RT2880_CHIP_NAME1`, `CHIP_ID_ID_MASK`, `CHIP_ID_ID_SHIFT`, `CHIP_ID_REV_MASK`, `RT2880_SDRAM_BASE`, `RT2880_MEM_SIZE_MIN`, `RT2880_MEM_SIZE_MAX`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `SYSC_REG (4)`, `CHIP_ID (3)`, `RT2880_CHIP (2)`, `RT2880_MEM (2)`, `IOMEM (1)`, `RT2880_SDRAM (1)`, `RT2880_SYSC (1)`, `_RT288X (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt288x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt288x/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt288x/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt288x/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ralink/rt288x`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 29 macros including `_RT288X_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_sb1_cache`, `cpu_has_fpu`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_prefetch`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_mips16`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `cpu_has_mips32r1`, `cpu_has_mips32r2`, `cpu_has_mips64r1`, `cpu_has_mips64r2`, `cpu_has_dsp`, `cpu_has_mipsmt`, and 5 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (26)`, `_RT288X (1)`, `cpu_dcache (1)`, `cpu_icache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt288x/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt305x.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt305x.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt305x.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-ralink`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 56 macros including `_RT305X_REGS_H_`, `IOMEM`, `RT305X_SYSC_BASE`, `SYSC_REG_CHIP_NAME0`, `SYSC_REG_CHIP_NAME1`, `SYSC_REG_CHIP_ID`, `SYSC_REG_SYSTEM_CONFIG`, `RT3052_CHIP_NAME0`, `RT3052_CHIP_NAME1`, `RT3350_CHIP_NAME0`, `RT3350_CHIP_NAME1`, `RT3352_CHIP_NAME0`, `RT3352_CHIP_NAME1`, `RT5350_CHIP_NAME0`, `RT5350_CHIP_NAME1`, `CHIP_ID_ID_MASK`, `CHIP_ID_ID_SHIFT`, `CHIP_ID_REV_MASK`, `RT305X_SYSCFG_SRAM_CS0_MODE_SHIFT`, `RT305X_SYSCFG_SRAM_CS0_MODE_WDT`, `RT5350_SYSCFG0_DRAM_SIZE_SHIFT`, `RT5350_SYSCFG0_DRAM_SIZE_MASK`, `RT5350_SYSCFG0_DRAM_SIZE_2M`, `RT5350_SYSCFG0_DRAM_SIZE_8M`, and 32 more; 0 structs: none; 0 enums: none; 6 callable helpers/prototypes: `soc_is_rt3050`, `soc_is_rt3052`, `soc_is_rt305x`, `soc_is_rt3350`, `soc_is_rt3352`, `soc_is_rt5350`; 1 extern variables: `ralink_soc`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `soc_is_rt3050`, `soc_is_rt3052`, `soc_is_rt305x`, `soc_is_rt3350`, `soc_is_rt3352`, `soc_is_rt5350`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `RT305X_GPIO (17)`, `RT5350_SYSCFG0 (7)`, `RT3352_SYSC (4)`, `SYSC_REG (4)`, `CHIP_ID (3)`, `RT3052_CHIP (2)`, `RT305X_MEM (2)`, `RT305X_SYSCFG (2)`. Typed contracts include no structs. Callable helpers or declarations include `soc_is_rt3050`, `soc_is_rt3052`, `soc_is_rt305x`, `soc_is_rt3350`, `soc_is_rt3352`, `soc_is_rt5350`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt305x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt305x/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt305x/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt305x/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ralink/rt305x`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 29 macros including `_RT305X_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_sb1_cache`, `cpu_has_fpu`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_prefetch`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_mips16`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `cpu_has_mips32r1`, `cpu_has_mips32r2`, `cpu_has_mips64r1`, `cpu_has_mips64r2`, `cpu_has_dsp`, `cpu_has_mipsmt`, and 5 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (26)`, `_RT305X (1)`, `cpu_dcache (1)`, `cpu_icache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt305x/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt3883.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt3883.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt3883.h` maps SoC register blocks, offsets, bit fields, and reset/clock identifiers for `mach-ralink`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 182 macros including `_RT3883_REGS_H_`, `IOMEM`, `RT3883_SDRAM_BASE`, `RT3883_SYSC_BASE`, `RT3883_TIMER_BASE`, `RT3883_INTC_BASE`, `RT3883_MEMC_BASE`, `RT3883_UART0_BASE`, `RT3883_PIO_BASE`, `RT3883_FSCC_BASE`, `RT3883_NANDC_BASE`, `RT3883_I2C_BASE`, `RT3883_I2S_BASE`, `RT3883_SPI_BASE`, `RT3883_UART1_BASE`, `RT3883_PCM_BASE`, `RT3883_GDMA_BASE`, `RT3883_CODEC1_BASE`, `RT3883_CODEC2_BASE`, `RT3883_FE_BASE`, `RT3883_ROM_BASE`, `RT3883_USBDEV_BASE`, `RT3883_PCI_BASE`, `RT3883_WLAN_BASE`, and 157 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `linux/bitops.h`. Major macro families are `RT3883_GPIO (51)`, `RT3883_RSTCTRL (21)`, `RT3883_SYSC (18)`, `RT3883_INTC (16)`, `RT3883_FSCC (6)`, `RT3883_FLASH (5)`, `RT3883_SYSCFG1 (5)`, `RT3883_CLKCFG1 (4)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is board setup, clock/reset drivers, pinctrl, IRQ, Ethernet, PCI, USB, serial, SPI, watchdog, and other platform devices.

## Risks
register definitions are executable hardware ABI; a single wrong offset or bit can reset, clock-gate, or misconfigure a peripheral; the file contains 182 macros, so broad edits have high review cost and should be grouped by register block or bit-field family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt3883.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt3883/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt3883/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt3883/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ralink/rt3883`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 29 macros including `_RT3883_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_sb1_cache`, `cpu_has_fpu`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_prefetch`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_mips16`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `cpu_has_mips32r1`, `cpu_has_mips32r2`, `cpu_has_mips64r1`, `cpu_has_mips64r2`, `cpu_has_dsp`, `cpu_has_mipsmt`, and 5 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (26)`, `_RT3883 (1)`, `cpu_dcache (1)`, `cpu_icache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/rt3883/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/spaces.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/spaces.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/spaces.h` overrides virtual/physical address-space constants for `mach-ralink`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `__ASM_MACH_RALINK_SPACES_H_`, `PCI_IOBASE`, `PCI_IOSIZE`, `IO_SPACE_LIMIT`, `pci_remap_iospace`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/spaces.h`. Major macro families are `IO_SPACE (1)`, `PCI_IOBASE (1)`, `PCI_IOSIZE (1)`, `_ (1)`, `pci_remap (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the MIPS memory layout headers, fixmap/ioremap code, PCI I/O windows, and early boot address translation.

## Risks
bad base addresses or limits can make the kernel map RAM, uncached MMIO, or PCI I/O through the wrong segment; address-space changes can affect every driver using `readl`/`writel`, `ioremap`, PCI I/O, or uncached aliases.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise early boot, PCI/SoC MMIO drivers, and uncached register access with `CONFIG_DEBUG_VIRTUAL` or ioremap debug checks when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ralink/spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 37 macros including `__ASM_MACH_RC32434_CPU_FEATURE_OVERRIDES_H`, `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_3k_cache`, `cpu_has_4k_cache`, `cpu_has_sb1_cache`, `cpu_has_fpu`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_watch`, `cpu_has_divec`, `cpu_has_vce`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_prefetch`, `cpu_has_mcheck`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_mdmx`, `cpu_has_mips3d`, `cpu_has_smartmips`, `cpu_has_vtag_icache`, and 13 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `cpu_has (34)`, `_ (1)`, `cpu_dcache (1)`, `cpu_icache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/cpu-feature-overrides.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/ddr.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/ddr.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/ddr.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 74 macros including `_ASM_RC32434_DDR_H_`, `DDR0_PHYS_ADDR`, `DDR_MASK`, `DDR0_BASE_MSK`, `DDR1_BASE_MSK`, `RC32434_DDR0_ATA_BIT`, `RC32434_DDR0_ATA_MSK`, `RC32434_DDR0_DBW_BIT`, `RC32434_DDR0_DBW_MSK`, `RC32434_DDR0_WR_BIT`, `RC32434_DDR0_WR_MSK`, `RC32434_DDR0_PS_BIT`, `RC32434_DDR0_PS_MSK`, `RC32434_DDR0_DTYPE_BIT`, `RC32434_DDR0_DTYPE_MSK`, `RC32434_DDR0_RFC_BIT`, `RC32434_DDR0_RFC_MSK`, `RC32434_DDR0_RP_BIT`, `RC32434_DDR0_RP_MSK`, `RC32434_DDR0_AP_BIT`, `RC32434_DDR0_AP_MSK`, `RC32434_DDR0_RCD_BIT`, `RC32434_DDR0_RCD_MSK`, `RC32434_DDR0_CL_BIT`, and 50 more; 1 structs: `ddr_ram`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `ddr_ram` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are `asm/mach-rc32434/rb.h`. Major macro families are `RC32434_DDR0 (28)`, `RC32434_LLC (10)`, `RC32434_QSC (10)`, `RC32434_DCST (6)`, `RC32434_LLFC (4)`, `RC32434_DDRC (3)`, `RC32434_DLLED (3)`, `RC32434_DSCT (3)`. Typed contracts include `ddr_ram`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/ddr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 45 macros including `__ASM_RC32434_DMA_H`, `DMA0_BASE_ADDR`, `DMA_DESC_SIZ`, `DMA_DESC_COUNT_BIT`, `DMA_DESC_COUNT_MSK`, `DMA_DESC_DS_BIT`, `DMA_DESC_DS_MSK`, `DMA_DESC_DEV_CMD_BIT`, `DMA_DESC_DEV_CMD_MSK`, `DMA_DESC_DEV_CMD_BYTE`, `DMA_DESC_DEV_CMD_HLF_WD`, `DMA_DESC_DEV_CMD_WORD`, `DMA_DESC_DEV_CMD_2WORDS`, `DMA_DESC_DEV_CMD_4WORDS`, `DMA_DESC_DEV_CMD_6WORDS`, `DMA_DESC_DEV_CMD_8WORDS`, `DMA_DESC_DEV_CMD_16WORDS`, `DMA_DESC_COF`, `DMA_DESC_COD`, `DMA_DESC_IOF`, `DMA_DESC_IOD`, `DMA_DESC_TERM`, `DMA_DESC_DONE`, `DMA_DESC_FINI`, and 21 more; 4 structs: `dma_desc`, `dma_reg`, `dma_channel`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `dma_desc`, `dma_reg`, `dma_channel` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are `asm/mach-rc32434/rb.h`. Major macro families are `DMA_DESC (22)`, `DMA_CHAN (16)`, `DMA_STAT (5)`, `DMA0_BASE (1)`, `_ (1)`. Typed contracts include `dma_desc`, `dma_reg`, `dma_channel`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma_v.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma_v.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma_v.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `_ASM_RC32434_DMA_V_H_`, `DMA_CHAN_OFFSET`, `IS_DMA_USED`, `DMA_COUNT`, `DMA_HALT_TIMEOUT`; 0 structs: none; 0 enums: none; 4 callable helpers/prototypes: `rc32434_halt_dma`, `rc32434_start_dma`, `rc32434_chain_dma`, `__raw_writel`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `rc32434_halt_dma`, `rc32434_start_dma`, `rc32434_chain_dma`, `__raw_writel`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm/mach-rc32434/dma.h`, `asm/mach-rc32434/rc32434.h`. Major macro families are `DMA_CHAN (1)`, `DMA_COUNT (1)`, `DMA_HALT (1)`, `IS_DMA (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include `rc32434_halt_dma`, `rc32434_start_dma`, `rc32434_chain_dma`, `__raw_writel`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/dma_v.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/eth.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/eth.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/eth.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 101 macros including `__ASM_RC32434_ETH_H`, `ETH0_BASE_ADDR`, `ETH_INT_FC_EN`, `ETH_INT_FC_ITS`, `ETH_INT_FC_RIP`, `ETH_INT_FC_JAM`, `ETH_INT_FC_OVR`, `ETH_INT_FC_UND`, `ETH_INT_FC_IOC`, `ETH_FIFI_TT_TTH_BIT`, `ETH_FIFO_TT_TTH`, `ETH_ARC_PRO`, `ETH_ARC_AM`, `ETH_ARC_AFM`, `ETH_ARC_AB`, `ETH_SAL_BYTE_5`, `ETH_SAL_BYTE_4`, `ETH_SAL_BYTE_3`, `ETH_SAL_BYTE_2`, `ETH_SAH_BYTE1`, `ETH_SAH_BYTE0`, `ETH_GPF_PTV`, `ETH_PFS_PFD`, `ETH_CFSA0_CFSA4`, and 77 more; 1 structs: `eth_regs`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `eth_regs` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `ETH_TX (18)`, `ETH_RX (17)`, `ETH_MAC2 (13)`, `ETH_MII (10)`, `ETH_INT (7)`, `ETH_MAC1 (6)`, `ETH_ARC (4)`, `ETH_CFSA1 (4)`. Typed contracts include `eth_regs`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; the file contains 101 macros, so broad edits have high review cost and should be grouped by register block or bit-field family; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/gpio.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/gpio.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/gpio.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 21 macros including `_RC32434_GPIO_H_`, `RC32434_UART0_SOUT`, `RC32434_UART0_SIN`, `RC32434_UART0_RTS`, `RC32434_UART0_CTS`, `RC32434_MP_BIT_22`, `RC32434_MP_BIT_23`, `RC32434_MP_BIT_24`, `RC32434_MP_BIT_25`, `RC32434_CPU_GPIO`, `RC32434_AF_SPARE_6`, `RC32434_AF_SPARE_4`, `RC32434_AF_SPARE_3`, `RC32434_AF_SPARE_2`, `RC32434_PCI_MSU_GPIO`, `GPIO_RDY`, `GPIO_WPX`, `GPIO_ALE`, `GPIO_CLE`, `CF_GPIO_NUM`, `GPIO_BTN_S1`; 1 structs: `rb532_gpio_reg`; 0 enums: none; 3 callable helpers/prototypes: `rb532_gpio_set_ilevel`, `rb532_gpio_set_istat`, `rb532_gpio_set_func`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `rb532_gpio_set_ilevel`, `rb532_gpio_set_istat`, `rb532_gpio_set_func`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `RC32434_AF (4)`, `RC32434_MP (4)`, `RC32434_UART0 (4)`, `CF_GPIO (1)`, `GPIO_ALE (1)`, `GPIO_BTN (1)`, `GPIO_CLE (1)`, `GPIO_RDY (1)`. Typed contracts include `rb532_gpio_reg`. Callable helpers or declarations include `rb532_gpio_set_ilevel`, `rb532_gpio_set_istat`, `rb532_gpio_set_func`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/integ.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/integ.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/integ.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 14 macros including `__RC32434_INTEG_H__`, `INTEG0_BASE_ADDR`, `RC32434_ERR_WTO`, `RC32434_ERR_WNE`, `RC32434_ERR_UCW`, `RC32434_ERR_UCR`, `RC32434_ERR_UPW`, `RC32434_ERR_UPR`, `RC32434_ERR_UDW`, `RC32434_ERR_UDR`, `RC32434_ERR_SAE`, `RC32434_ERR_WRE`, `RC32434_WTC_EN`, `RC32434_WTC_TO`; 1 structs: `integ`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `integ` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are `asm/mach-rc32434/rb.h`. Major macro families are `RC32434_ERR (10)`, `RC32434_WTC (2)`, `INTEG0_BASE (1)`, `_ (1)`. Typed contracts include `integ`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/integ.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/irq.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/irq.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/irq.h` defines IRQ number layout and interrupt-controller constants for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 18 macros including `__ASM_RC32434_IRQ_H`, `NR_IRQS`, `IC_GROUP0_PEND`, `IC_GROUP0_MASK`, `IC_GROUP_OFFSET`, `NUM_INTR_GROUPS`, `GROUP0_IRQ_BASE`, `GROUP1_IRQ_BASE`, `GROUP2_IRQ_BASE`, `GROUP3_IRQ_BASE`, `GROUP4_IRQ_BASE`, `UART0_IRQ`, `ETH0_DMA_RX_IRQ`, `ETH0_DMA_TX_IRQ`, `ETH0_RX_OVR_IRQ`, `ETH0_TX_UND_IRQ`, `GPIO_MAPPED_IRQ_BASE`, `GPIO_MAPPED_IRQ_GROUP`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/mach-generic/irq.h`, `asm/mach-rc32434/rb.h`. Major macro families are `ETH0_DMA (2)`, `GPIO_MAPPED (2)`, `IC_GROUP0 (2)`, `ETH0_RX (1)`, `ETH0_TX (1)`, `GROUP0_IRQ (1)`, `GROUP1_IRQ (1)`, `GROUP2_IRQ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is arch IRQ initialization, irqchip drivers, cascaded interrupt controllers, board files, and device platform data.

## Risks
overlapping bases or stale `NR_IRQS` values can route device interrupts to the wrong Linux IRQ; IRQ base changes require matching irqchip, device-tree, and board-platform updates.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; verify `/proc/interrupts`, cascaded controller probing, and device IRQ delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/pci.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/pci.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 278 macros including `_ASM_RC32434_PCI_H_`, `epld_mask`, `PCI0_BASE_ADDR`, `PCI_LBA_COUNT`, `PCI_MSU_COUNT`, `PCI_CTL_EN`, `PCI_CTL_TNR`, `PCI_CTL_SCE`, `PCI_CTL_IEN`, `PCI_CTL_AAA`, `PCI_CTL_EAP`, `PCI_CTL_PCIM_BIT`, `PCI_CTL_PCIM`, `PCI_CTL_PCIM_DIS`, `PCI_CTL_PCIM_TNR`, `PCI_CTL_PCIM_SUS`, `PCI_CTL_PCIM_EXT`, `PCI_CTL`, `PCI_CTL_PCIM_RR`, `PCI_CTL_PCIM_RSVD6`, `PCI_CTL_PCIM_RSVD7`, `PCI_CTL_IGM`, `PCI_STAT_EED`, `PCI_STAT_WR`, and 251 more; 3 structs: `pci_map`, `pci_reg`, `pci_msu`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `pci_map`, `pci_reg`, `pci_msu` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `PCI_CFGA (30)`, `PCI_CFG04 (18)`, `PCI_STAT (18)`, `PCI_STATM (18)`, `PCI_CTL (17)`, `PCI_PBAC (14)`, `PCI_DMAD (10)`, `PCI_LBAC (9)`. Typed contracts include `pci_map`, `pci_reg`, `pci_msu`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; the file contains 278 macros, so broad edits have high review cost and should be grouped by register block or bit-field family; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/prom.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/prom.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/prom.h` declares board, firmware, memory, and platform-data contracts for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 9 macros including `PROM_ENTRY`, `SR_NMI`, `SERIAL_SPEED_ENTRY`, `FREQ_TAG`, `KMAC_TAG`, `MEM_TAG`, `BOARD_TAG`, `BOARD_RB532`, `BOARD_RB532A`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `BOARD_RB532 (1)`, `BOARD_RB532A (1)`, `BOARD_TAG (1)`, `FREQ_TAG (1)`, `KMAC_TAG (1)`, `MEM_TAG (1)`, `PROM_ENTRY (1)`, `SERIAL_SPEED (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/prom.h -->

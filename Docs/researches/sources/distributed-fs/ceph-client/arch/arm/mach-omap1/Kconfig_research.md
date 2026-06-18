<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Kconfig

Purpose: Configuration tree for legacy TI OMAP1 platforms. It selects shared OMAP infrastructure, timers, GPIO, IRQ chips, board types, mux support, clock reset options, serial wake, and board-specific dependencies.

Important APIs/types/functions: Important symbols include `ARCH_OMAP1`, `ARCH_OMAP15XX`, `ARCH_OMAP16XX`, `OMAP_MUX`, `OMAP_32K_TIMER`, `OMAP_MPU_TIMER`, and board symbols for OSK, PalmTE, SX1, Nokia770, and AMS Delta.

Control flow, state, and persistence: No runtime state exists, but selected symbols determine machine descriptors, timers, PM, FIQ, regulators, and device objects.

Dependencies and integration points: Important symbols include `ARCH_OMAP1`, `ARCH_OMAP15XX`, `ARCH_OMAP16XX`, `OMAP_MUX`, `OMAP_32K_TIMER`, `OMAP_MPU_TIMER`, and board symbols for OSK, PalmTE, SX1, Nokia770, and AMS Delta. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are legacy ATAGS dependency, mutually broad board selections, and drivers relying on selected clock/mux options. Test representative defconfigs for each board and PM/timer combinations.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 164 lines, 4532 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Kconfig -->

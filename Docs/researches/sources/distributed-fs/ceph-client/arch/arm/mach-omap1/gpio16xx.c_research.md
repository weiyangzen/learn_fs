<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio16xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio16xx.c

Purpose: OMAP16xx GPIO platform-device registration. It defines MPUIO plus four GPIO banks, initializes each bank's SYSCONFIG for smart idle/wakeup, and registers them before machine init.

Important APIs/types/functions: Important data includes `omap16xx_mpuio_regs`, `omap16xx_gpio_regs`, five platform devices, and `omap16xx_gpio_init`.

Control flow, state, and persistence: State is static resources/platform data plus transient ioremaps used to write SYSCONFIG before device registration. Runtime state moves to gpio-omap.

Dependencies and integration points: Important data includes `omap16xx_mpuio_regs`, `omap16xx_gpio_regs`, five platform devices, and `omap16xx_gpio_init`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP16xx register addresses, `ULPD_CAM_CLK_CTRL` system-clock enable, IRQ numbers, and CPU detection. Risks are ioremap failure aborting later banks, hard-coded CAM clock control for GPIO, and early GPIO consumers relying on labels. Test all GPIO bank labels/IRQs, wakeup, smart idle, and non-16xx builds.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 251 lines, 6136 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio16xx.c -->

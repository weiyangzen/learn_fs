<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio15xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio15xx.c

Purpose: OMAP15xx GPIO platform-device registration. It describes the MPU IO GPIO bank and the OMAP1510 GPIO bank register offsets/resources and registers them before machine init.

Important APIs/types/functions: Important data includes `omap15xx_mpuio_regs`, `omap15xx_gpio_regs`, `omap15xx_mpu_gpio`, `omap15xx_gpio`, and `omap15xx_gpio_init` as a `postcore_initcall`.

Control flow, state, and persistence: State is static platform data/resources. Runtime GPIO state is owned by the gpio-omap driver after registration.

Dependencies and integration points: Important data includes `omap15xx_mpuio_regs`, `omap15xx_gpio_regs`, `omap15xx_mpu_gpio`, `omap15xx_gpio`, and `omap15xx_gpio_init` as a `postcore_initcall`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP1 MPUIO/GPIO register definitions, IRQ numbers, and `cpu_is_omap15xx`. Risks are early registration ordering and register offset coupling with AMS Delta FIQ code. Test GPIO numbering, IRQs, keypad/modem/NAND GPIO consumers, and non-15xx no-op behavior.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 116 lines, 2813 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio15xx.c -->

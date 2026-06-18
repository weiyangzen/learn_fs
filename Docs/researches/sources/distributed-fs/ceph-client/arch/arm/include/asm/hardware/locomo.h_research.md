# sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/locomo.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/locomo.h` declares Sharp LoCoMo
companion-chip registers, subdevice IDs, and driver helper APIs. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARCH_LOCOMO`, `locomo_writel`, `locomo_readl`, `LOCOMO_VER`, `LOCOMO_ST`,
`LOCOMO_C32K`, `LOCOMO_ICR`, `LOCOMO_MCSX0`, `LOCOMO_MCSX1`, `LOCOMO_MCSX2`, `LOCOMO_MCSX3`,
`LOCOMO_ASD`, `LOCOMO_HSD`, `LOCOMO_HSC`, `LOCOMO_TADC`, `LOCOMO_LTC`, `LOCOMO_LTINT`, `LOCOMO_DAC`,
and 99 more; types: `locomo_dev`, `device`, `locomo_driver`, `device_driver`,
`locomo_platform_data`; functions/prototypes: `locomolcd_power`, `locomo_driver_register`,
`locomo_driver_unregister`, `locomo_gpio_set_dir`, `locomo_gpio_read_level`,
`locomo_gpio_read_output`, `locomo_gpio_write`, `locomo_m62332_senddata`, `locomo_frontlight_set`.
The file is 217 lines / 7083 bytes, and the exported surface is primarily an include-time contract
for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `locomo_dev`, `device`, `locomo_driver`, `device_driver`,
`locomo_platform_data`. External state or implementation hooks include `locomolcd_power`. DMA-
visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the DMA
mapping or driver layers. There is no userspace filesystem persistence in this file; persistence is
either kernel memory, CPU register state, hardware register state, or generated ABI values. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. Interrupt-related declarations integrate with generic irqchip,
exception entry, and per-CPU irq accounting code. DMA paths integrate with cache maintenance, IOMMU,
scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `locomo.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.

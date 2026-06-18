# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_cpu.h

**Purpose:** Central BCM63xx CPU identity, register-set address, IRQ mapping, and machine-control contract.

**Important APIs/types/functions:** Defines CPU IDs for BCM3368/6328/6338/6345/6348/6358/6362/6368, `bcm63xx_cpu_init()`, `bcm63xx_get_cpu_rev()`, `bcm63xx_get_cpu_freq()`, global `bcm63xx_cpu_id`, `bcm63xx_get_cpu_id()`, `BCMCPU_IS_*()` predicates, `enum bcm63xx_regs_set`, register-set size macros, per-CPU base address constants, `bcm63xx_regs_base`, `__GEN_CPU_REGS_TABLE()`, `bcm63xx_regset_address()`, `enum bcm63xx_irq`, per-CPU IRQ constants including high IRQ banks, `bcm63xx_irqs`, `__GEN_CPU_IRQ_TABLE()`, `bcm63xx_get_irq_number()`, `bcm63xx_get_memory_size()`, `bcm63xx_machine_halt()`, and `bcm63xx_machine_reboot()`.

**Control flow:** CPU init identifies silicon and selects the active register-base and IRQ tables. Device registration and IO helpers query `bcm63xx_regset_address()` and `bcm63xx_get_irq_number()` so drivers can remain SoC-neutral. CPU predicates gate feature-specific paths. Halt/reboot functions are used by machine operations.

**State and persistence behavior:** Global CPU ID, register-base table pointer, and IRQ table pointer persist after early init. The header maps absent blocks to `0xdeadbeef` or zero IRQs, so callers must gate unsupported resources.

**Dependencies and integration points:** Depends on Linux types/init, Kconfig CPU options, `IRQ_INTERNAL_BASE` from `bcm63xx_irq.h` include ordering, and all BCM63xx platform device headers. It is consumed by IO, GPIO, flash, SPI, Ethernet, PCI, USB, timer, watchdog, and memory code.

**Risks:** Table entries are long and repetitive; a single wrong base/IRQ can break a device only on one SoC. Unsupported placeholders can become real bad MMIO accesses if callers skip feature checks. `unreachable()` in unsupported CPU ID paths assumes Kconfig and runtime ID cannot disagree.

**Test signals:** Build every CPU Kconfig combination, boot all supported SoCs, verify `/proc/cpuinfo`, memory size, register resources, IRQ tables, timer/watchdog/UART, PCI/USB/Ethernet/SPI, and assert no driver maps `0xdeadbeef` resources.

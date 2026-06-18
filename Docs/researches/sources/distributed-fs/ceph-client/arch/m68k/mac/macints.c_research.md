# sources/distributed-fs/ceph-client/arch/m68k/mac/macints.c

## Purpose
Defines the Macintosh m68k IRQ chip and dispatches generic Mac interrupt enable/disable operations to VIA, OSS, PSC, and Baboon hardware layers.

## APIs, Flow, And State
`mac_init_IRQ()` installs a `mac_irq_chip` over machine-specific IRQ sources, chains the hardware dispatchers for VIA or OSS, PSC, Baboon, and IOP, and registers level-7 NMI handling. `mac_irq_enable()` and `mac_irq_disable()` inspect `IRQ_SRC(irq)` and call the appropriate controller-specific mask functions. `mac_irq_startup()` and `mac_irq_shutdown()` special-case NuBus slot IRQs on non-OSS systems to use VIA NuBus startup/shutdown semantics. The NMI handler uses a static recursion guard and dumps registers.

## Dependencies And Integration
Depends on Mac IRQ numbering, VIA/OSS/PSC/IOP/Baboon globals and registration functions, m68k IRQ controller setup, `get_irq_regs()`, and processor debug helpers. It is called through `mach_init_IRQ` installed by `config_mac()`.

## Risks And Test Signals
The switch-based routing assumes IRQ source encoding remains stable. NuBus and Baboon interrupts are nested through multiple chained handlers, so incorrect masking can lose shared interrupts or create storms. Test signals include timer, ADB, SCSI, SCC, NuBus, PSC, OSS, and NMI behavior on the relevant model families.

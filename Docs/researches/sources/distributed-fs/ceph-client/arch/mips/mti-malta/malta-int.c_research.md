<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-int.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-int.c

### Purpose
`malta-int.c` initializes Malta interrupt routing and handles fatal CoreHi interrupts.

### Important APIs, Types, And Functions
`arch_init_irq()` reserves i8259 virtual IRQs, sets i8259 poll callback, calls `irqchip_init()`, initializes MSC IRQ maps, chooses CoreHi IRQ routing, and requests the CoreHi handler. `mips_pcibios_iack()` performs controller-specific PCI IACK. `corehi_irqdispatch()` dumps controller state and calls `die()`.

### Control Flow
Boot reserves the legacy i8259 range before other irqchips allocate descriptors. PCI IACK is routed through MSC, GT64120, or Bonito registers based on `mips_revision_sconid`. MSC interrupt controllers are initialized differently for VEIC and non-VEIC modes. CoreHi is wired through GIC, VEIC handler, or CPU IRQ and registered as a non-threaded interrupt.

### State, Persistence, And Dependencies
State includes reserved IRQ descriptors, i8259 poll function, MSC interrupt controller setup, and registered CoreHi IRQ action. Dependencies include irqchip DT probing, Malta revision globals, i8259, MSC01, GT64120, Bonito, GIC, VEIC, and exception register access.

### Integration Points
This file connects platform interrupt hardware to Linux IRQ domains and legacy i8259 behavior. It relies on `malta-init.c` controller detection and FDT shim interrupt topology.

### Risks
If i8259 descriptors are not reserved early, irqchip probing can allocate conflicting virqs. Bonito PCI IACK uses a special config mapping sequence and IO barriers. CoreHi is treated as fatal, so false routing to CoreHi halts the system.

### Test Signals
Boot with GIC, VEIC, and legacy CPU interrupt modes; verify i8259 IRQ allocation, PCI interrupts, timer/perf IRQs, and deliberate CoreHi diagnostics on hardware or emulator support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-int.c -->

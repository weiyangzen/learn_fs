<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-rd88f5182.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-rd88f5182.c

### Purpose
`board-rd88f5182.c` provides PCI IRQ setup for the Marvell RD-88F5182 NAS reference design under DT.

### Important APIs, Types, And Functions
Key functions are `rd88f5182_pci_preinit()`, `rd88f5182_pci_map_irq()`, and `rd88f5182_pci_init()`, plus the `rd88f5182_pci` `hw_pci` descriptor.

### Control Flow
Subsystem PCI init checks the DT compatible string. Preinit requests GPIOs for PCI IntA/IntB and configures them as level-low IRQ inputs. IRQ mapping uses common Orion PCIe mapping first, then maps slot 0 pin A/B to the configured GPIO IRQs.

### State, Persistence, And Dependencies
State persists in GPIO requests, IRQ trigger type, and PCI host registration. Dependencies include OF machine matching, common Orion PCI setup, and GPIO-to-IRQ mapping.

### Integration Points
This file complements `board-dt.c` for the `marvell,rd-88f5182-nas` compatible.

### Risks
GPIO setup errors only log, but IRQ mapping may still return GPIO IRQ numbers. Slot offset assumptions are board-specific.

### Test Signals
Boot on RD-88F5182 should initialize PCI and route slot 0 interrupts through GPIO 7 and 6 as level-low interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-rd88f5182.c -->

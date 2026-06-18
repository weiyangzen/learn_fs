<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irqs.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irqs.h

### Purpose
`irqs.h` assigns Linux IRQ numbers for Orion5x main interrupt sources and GPIO interrupts.

### Important APIs, Types, And Functions
It defines constants for bridge, UART, I2C, GPIO groups, PCIe/PCI, USB, Ethernet, IDMA, CESA, SATA, XOR, `IRQ_ORION5X_GPIO_START`, `NR_GPIO_IRQS`, and `ORION5X_NR_IRQS`.

### Control Flow
There is no executable flow; this is a numbering contract.

### State, Persistence, And Dependencies
The header has no state. Values are consumed by common init, IRQ setup, peripheral registration, and board files.

### Integration Points
Machine descriptors use `ORION5X_NR_IRQS`, and platform devices use individual IRQ constants.

### Risks
IRQ numbers are one-based for main controller lines; changing them would break platform data and drivers.

### Test Signals
Boot and peripheral interrupt tests validate that each platform device receives the right IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/irqs.h -->

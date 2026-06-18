## sources/distributed-fs/ceph-client/arch/mips/pci/pci-ip32.c

### Purpose
This file initializes the SGI O2/IP32 MACE PCI host bridge, installs an error interrupt handler, sets global I/O and memory resource bounds, and registers the MACE PCI controller.

### Important APIs, Types, And Functions
`macepci_error()` decodes MACE PCI error bits for master/target aborts, parity, retry, illegal command, SERR, overrun, and interrupt-test conditions, then clears handled bits. Static resources define 32-bit and 64-bit memory windows. `mace_pci_controller` binds external `mace_pci_ops` to resources. `mace_init()` performs boot setup.

### Control Flow
At `arch_initcall()`, `mace_init()` sets `PCIBIOS_MIN_IO`, clears error address/status, enables bridge error interrupts, logs revision, requests `MACE_PCI_BRIDGE_IRQ`, extends global resource limits, and calls `register_pci_controller()`. Later errors are reported by the IRQ handler.

### State, Persistence, And Dependencies
State lives in MACE MMIO registers and global PCI resources. Dependencies include IP32 MACE register definitions, interrupt constants, generic MIPS PCI controller registration, and `mace_pci_ops`.

### Integration Points
This file provides the host-controller registration; platform IRQ fixup and config operations are elsewhere. It integrates with the generic PCI scan after controller registration.

### Risks
`BUG_ON(request_irq())` panics if the bridge error IRQ cannot be installed. Error handling only logs and clears bits; some conditions may warrant stronger recovery. Resource ranges differ materially between 32-bit and 64-bit builds.

### Test Signals
Boot should print the MACE PCI revision, enumerate O2 PCI devices, and log bridge errors when forced by bad config/MMIO cycles without hanging.

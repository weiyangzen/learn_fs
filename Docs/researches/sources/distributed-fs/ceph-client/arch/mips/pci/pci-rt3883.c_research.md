## sources/distributed-fs/ceph-client/arch/mips/pci/pci-rt3883.c

### Purpose
This file implements the RT3662/RT3883 combined PCI/PCIe host controller. It detects desired PCI/PCIe mode from device-tree children, initializes clocks/resets, implements config access, creates a PCI interrupt domain, configures bridge BARs, and registers a legacy PCI controller.

### Important APIs, Types, And Functions
`struct rt3883_pci_controller` holds MMIO base, interrupt-controller node/domain, resources, embedded `pci_controller`, and `pcie_ready`. Helpers read/write controller registers and config space. IRQ support includes `rt3883_pci_irq_handler()`, mask/unmask methods, `rt3883_pci_irq_map()`, and `rt3883_pci_irq_init()`. Hardware setup is in `rt3883_pci_preinit()` and `rt3883_pci_probe()`.

### Control Flow
Probe allocates controller state, maps MMIO, locates interrupt-controller and PCI host child nodes, inspects child PCI devfn slots to decide PCI, PCIe, or both, runs preinit to reset/clock selected blocks and verify PCIe link, fills PCI ops/resources, loads OF ranges, programs MEM/IO bases and root-complex identity/class registers, creates an IRQ domain, enables command bits for PCIe and PCI root functions, adjusts BAR/P2P bridge registers depending on mode, and registers the controller.

### State, Persistence, And Dependencies
State persists in controller registers, sysc reset/clock registers, IRQ domain mappings, OF node references, `pcie_ready`, and PCI resources. Dependencies include RT3883 sysc register definitions, irqdomain APIs, OF PCI parsing, and legacy PCI core.

### Integration Points
The driver matches `"ralink,rt3883-pci"` and maps PCI IRQs with `of_irq_parse_and_map_pci()`. It can expose conventional PCI slots, PCIe slot, or both based on DT topology.

### Risks
OF child references must be released on error; the success path relies on device lifetime. Config access to bus 1 is blocked when PCIe link is absent. Mode detection depends on child slots matching expected devfn values. Interrupt handling processes all pending bits but spurious handling may hide masking bugs.

### Test Signals
Test PCI-only, PCIe-only, and combined modes; verify PCIe no-link disables access cleanly; confirm child interrupt domain mappings and OF IRQ parsing; enumerate devices behind the P2P bridge.

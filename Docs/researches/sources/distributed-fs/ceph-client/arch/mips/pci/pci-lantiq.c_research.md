## sources/distributed-fs/ceph-client/arch/mips/pci/pci-lantiq.c

### Purpose
This file implements the Lantiq XWAY PCI host controller platform driver. It maps PCI controller registers and config space, enables clocks, programs FCI/PCI address windows and arbitration, handles reset GPIO, loads device-tree ranges, and registers a legacy MIPS `pci_controller`.

### Important APIs, Types, And Functions
State includes `ltq_pci_mapped_cfg`, `ltq_pci_membase`, `reset_gpio`, `clk_pci`, `clk_external`, `pci_io_resource`, and `pci_mem_resource`. `ltq_calc_bar11mask()` computes the host BAR mask from system RAM size. `ltq_pci_startup()` performs hardware initialization. `ltq_pci_probe()` maps resources, starts hardware, loads OF ranges, and registers the controller. `pcibios_init()` registers the platform driver.

### Control Flow
Probe clears `PCI_PROBE_ONLY`, maps resource 1 as controller MMIO and resource 0 as config space, then calls startup. Startup obtains PCI and external clocks, optionally applies `lantiq,bus-clock`, enables or disables the external clock per DT, gets optional reset GPIO, enables PCI/EBU switching, enables bus-master/IO/memory bits in config space, programs request masks, address maps, BAR masks, endian swap, burst length, EBU IRQ routing, and toggles reset.

### State, Persistence, And Dependencies
Persistent state is in Lantiq PCI/CGU/EBU registers, clock state, reset line state, and registered PCI resources. Dependencies include Lantiq SoC MMIO helpers, Lantiq IRQ/EBU constants, OF PCI range parsing, GPIO descriptors, and config ops declared in `pci-lantiq.h`.

### Integration Points
The driver matches `"lantiq,pci-xway"` device-tree nodes and uses `pci_load_of_ranges()` from the legacy MIPS PCI code. Config access comes from Lantiq-specific ops in another source file.

### Risks
Startup errors after clock acquisition are not fully unwound. `ltq_pci_probe()` ignores the return value of `ltq_pci_startup()`, so failed GPIO or clock setup may still lead to registration. BAR mask calculation assumes a power-of-two memory envelope derived from `get_num_physpages()`.

### Test Signals
Device-tree boot should bind `pci-xway`, show correct ranges in `/proc/iomem`, enumerate PCI devices, observe reset GPIO toggling, and show working config reads through `ltq_pci_mapped_cfg`.

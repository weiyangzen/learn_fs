# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-mvebu.c

## Purpose
`pci-mvebu.c` is the PCIe controller driver for Marvell Armada 370/XP, Dove, and Kirkwood style SoCs. It models multiple hardware PCIe ports as root-port devices on a virtual bus 0, emulates bridge config space for those root ports, routes child config cycles to the correct hardware port, programs MBus address windows for PCI memory and I/O forwarding, manages legacy INTx domains, and handles port power/reset/clock lifecycles.

## Important APIs, types, and functions
`struct mvebu_pcie` stores global controller state, resource apertures, and the array of ports. `struct mvebu_pcie_port` stores per-port MMIO base, port/lane identity, devfn, MBus target/attribute values, clock/reset GPIO, emulated bridge, DT node, current memory/I/O windows, saved status, slot power limit, INTx domain, lock, and IRQ.

Hardware setup functions include `mvebu_pcie_setup_hw()`, which enables root-complex mode, fixes link width, disables command bits, changes the class code to PCI bridge, sets DRAM decode windows, programs slot power limit messaging, and masks/clears interrupts. `mvebu_pcie_setup_wins()` and `mvebu_pcie_disable_wins()` manage BAR/window registers for DRAM and internal-register access. `mvebu_pcie_child_rd_conf()` and `mvebu_pcie_child_wr_conf()` issue hardware config cycles for downstream devices after finding the owning port and checking link state.

Bridge emulation is provided by `pci-bridge-emul`. `mvebu_pci_bridge_emul_*_read()` and `*_write()` expose command, bus number, bridge control, PCIe capability, slot control/status, root status, and AER registers while translating selected writes into hardware side effects. `mvebu_pcie_handle_iobase_change()` and `mvebu_pcie_handle_membase_change()` convert emulated bridge window registers into MBus windows through `mvebu_pcie_set_window()`.

IRQ support is implemented with `mvebu_pcie_init_irq_domain()`, `mvebu_pcie_irq_handler()`, `mvebu_pcie_intx_irq_mask()`, and `mvebu_pcie_intx_irq_unmask()`. Each port can expose a four-entry INTx domain under a child interrupt-controller node; old bindings without a named `intx` interrupt fall back to unmasking all INTx bits in hardware.

## Control flow
Probe allocates a host bridge, parses/request global PCI memory and I/O apertures from MBus helper APIs, counts available child DT nodes, parses each port child, then powers up and maps only successfully parsed ports. Per-port parsing requires `marvell,pcie-port`, a valid devfn with function zero, MEM target/attribute information from parent ranges, optional I/O target/attribute, optional named `intx`, optional reset GPIO and delay, slot power limit, and a clock.

For each active port, probe enables the clock/reset sequence, maps registers, initializes bridge emulation, creates the INTx domain and chained handler when available, programs hardware, and sets local device/bus numbers to support the driver's virtual bus-0 topology. Finally it installs root `pci_ops` for emulated root ports, child ops for downstream config cycles, resource alignment, IRQ mapping, and calls `pci_host_probe()`.

Remove stops and removes the root bus, disables command bits and interrupts, removes chained handlers and IRQ domains, cleans up bridge emulation, disables slot power limit messaging, clears hardware windows, deletes any dynamically created MBus windows, and powers down each port. Suspend saves `PCIE_STAT_OFF`; resume restores it and reruns hardware setup for each mapped port.

## State and persistence behavior
The driver maintains per-port current `memwin` and `iowin` state to avoid redundant MBus reprogramming and to delete old windows before installing new ones. Bridge config state lives in the emulation buffers and is partially synchronized to hardware. Hardware state includes root-complex mode, link capability width, BAR/window registers, interrupt masks, slot power limit, local bus/device numbers, and saved status across system sleep. There is no disk persistence.

## Dependencies and integration points
The driver depends on DT child-node topology, `of_pci_get_devfn()`, MBus aperture/window APIs, `pci-bridge-emul`, common PCI host bridge probing, GPIO descriptors for PERST, clocks, IRQ domains/chained IRQ handling, and generic PCI resource assignment. It exports no MSI domain; MSI support would be through platform facilities outside this file, while legacy INTx is handled here.

## Risks and edge cases
The topology is intentionally nonstandard: multiple independent host bridges are presented as bridges on one virtual bus 0 for compatibility with historical DT bindings. Routing errors in `mvebu_pcie_find_port()` or bus-number emulation can break config access. Window changes are not atomic; `mvebu_pcie_set_window()` deletes old windows before adding new ones. MBus windows require power-of-two splits and alignment, so resource alignment is critical. Old DTs without `intx` cannot mask individual INTx lines and may incur shared-interrupt overhead. Partial port failures are skipped, so systems can boot with fewer active ports than described.

## Test signals
Validation should cover Armada/Dove/Kirkwood DT variants, x1 and x4 links, absent/down links, root-port bridge config reads/writes, child config access, memory and I/O window assignment and teardown, non-power-of-two BAR sizes, INTx domain mapping and mask/unmask, old DT fallback interrupts, reset GPIO timing, slot power limit programming, suspend/resume link recovery, and hot remove/module unload cleanup.

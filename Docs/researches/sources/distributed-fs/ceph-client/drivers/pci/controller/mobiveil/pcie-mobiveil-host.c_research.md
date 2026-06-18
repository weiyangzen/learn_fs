## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil-host.c

Purpose: Shared Mobiveil host-mode implementation. It provides PCI config access, DT resource parsing, root-port initialization, outbound/inbound window programming orchestration, INTx and MSI interrupt domains, integrated interrupt handling, and final `pci_host_probe()`.

Important APIs, types, and functions: `mobiveil_pcie_map_bus()` maps root-port DBI or endpoint config space, programming the config outbound window BDF fields for non-root accesses. `mobiveil_pcie_parse_dt()` maps `"config_axi_slave"` and `"csr_axi_slave"` and reads `apio-wins`/`ppio-wins`. `mobiveil_host_init()` sets bus numbers, command bits, PAB PIO enablement, config/inbound windows, DT memory/IO windows, and class code. Interrupt support includes `mobiveil_pcie_isr()`, `mobiveil_pcie_intx_map()`, mask/unmask callbacks, MSI parent domain ops, `mobiveil_compose_msi_msg()`, allocation/free, and `mobiveil_pcie_integrated_interrupt_init()`. `mobiveil_pcie_host_probe()` validates bridge header type, initializes host/windows/interrupts, assigns `bridge->sysdata` and ops, brings the link up, and calls `pci_host_probe()`.

Control flow: platform drivers allocate `struct pci_host_bridge` and embedded `mobiveil_pcie`, set `pdev`, optional PAB/root-port ops, and call this probe. The library parses resources, initializes hardware, initializes either platform-provided or integrated interrupts, waits for link, then hands off to generic PCI enumeration.

State and persistence: volatile state includes mapped CSR/config/APB bases, physical controller base for MSI messages, APIO/PPIO window counts, configured window counters, INTx/MSI irqdomains, MSI allocation bitmap, interrupt masks, and PAB register state. No persistent storage.

Dependencies and integration points: platform resources, Mobiveil CSR helpers from `pcie-mobiveil.c`, Linux MSI parent-domain library, irqdomain/chained IRQ, PCI host bridge, OF ranges/windows, and optional platform `interrupt_init`/`link_up` ops.

Risks: `mobiveil_pcie_map_bus()` relies on global PCI config serialization when reprogramming the shared config window. INTx hwirq values are one-based in handling but domain size is four, so mapping semantics must remain consistent. MSI has only 16 vectors. Host init increments window counters without failing when windows overflow; it logs but may leave resources unmapped.

Test signals: config reads across root and child buses, rejection of invalid root/direct-child slots, memory/IO window programming from DT, inbound 256 GiB window behavior, INTx routing, MSI allocation/exhaustion/free, link timeout handling, and platform override interrupt path.

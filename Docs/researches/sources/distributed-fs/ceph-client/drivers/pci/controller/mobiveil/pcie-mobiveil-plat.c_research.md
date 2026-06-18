## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil-plat.c

Purpose: Generic platform front end for Mobiveil AXI PCIe soft IP. It allocates a host bridge with Mobiveil private storage and delegates all real setup to the shared Mobiveil host probe.

Important APIs, types, and functions: `mobiveil_pcie_probe()` calls `devm_pci_alloc_host_bridge(dev, sizeof(*pcie))`, gets the private `struct mobiveil_pcie`, assigns `pcie->rp.bridge` and `pcie->pdev`, then returns `mobiveil_pcie_host_probe(pcie)`. The OF table matches `mbvl,gpex40-pcie`.

Control flow: platform probe is a thin adapter. Kbuild registers it as a built-in platform driver. Shared code handles DT resource mapping, interrupts, windows, link, and enumeration.

State and persistence: no local state beyond the embedded Mobiveil structure allocated as host-bridge private data. No persistent state.

Dependencies and integration points: Mobiveil host library, PCI host bridge allocation, OF platform matching, and the resources/properties expected by `pcie-mobiveil-host.c`.

Risks: There is no platform-specific `link_up` or `interrupt_init` override, so the generic IP must match the integrated interrupt and LTSSM behavior in the shared library. Remove/unwind is entirely devm/platform lifetime based.

Test signals: DT-compatible probe, host bridge allocation, successful shared probe using `"config_axi_slave"`, `"csr_axi_slave"`, and `"apb_csr"` resources, MSI/INTx interrupts through integrated path, and link-up via common LTSSM register.

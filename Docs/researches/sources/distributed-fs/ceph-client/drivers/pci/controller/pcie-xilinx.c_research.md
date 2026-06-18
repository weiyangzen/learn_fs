# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx.c

Purpose: Implements the older Xilinx AXI PCIe host controller driver. It maps controller/ECAM registers, validates config-space access by link state and root-port device number, handles legacy INTx and MSI through irqdomains, logs controller errors, initializes interrupts, enables the bridge, and registers a PCI host bridge.

Important APIs/types/functions: `struct xilinx_pcie` stores device, register base, MSI bitmap, map lock, MSI domain, legacy domain, and resources. Key functions include `xilinx_pcie_map_bus()`, `xilinx_allocate_msi_domains()`, `xilinx_pcie_init_irq_domain()`, `xilinx_pcie_intr_handler()`, `xilinx_pcie_init_port()`, `xilinx_pcie_parse_dt()`, and `xilinx_pcie_probe()`.

Control flow: Probe allocates the host bridge, initializes the MSI bitmap lock, maps the first `reg` resource with config semantics, requests the shared controller IRQ, initializes hardware interrupt masks and bridge-enable bit, creates legacy and optional MSI domains, assigns `xilinx_pcie_ops`, and calls `pci_host_probe()`. The single interrupt handler reads IDR and IMR, logs link/error causes, decodes INTx/MSI from root-port interrupt FIFO registers, dispatches to the appropriate domain, and clears IDR status.

State and persistence: Runtime state includes MSI bitmap allocations and irqdomains. Hardware state includes interrupt masks/status, MSI base registers programmed from the driver object page, and bridge-enable bit.

Dependencies/integration: Uses Linux PCI host bridge and generic config helpers, OF address/IRQ parsing, irqdomain, generic MSI library, and `pci_irqd_intx_xlate` for INTx.

Risks: MSI target address is `ALIGN_DOWN(virt_to_phys(pcie), SZ_4K)`, tying interrupt writes to the physical page containing driver data rather than a separately allocated DMA object. The top-level MSI ack is effectively a no-op because the shared interrupt handler already clears status. Downstream config access is inherently racy with link state. The driver supports only one device directly under the root port.

Test signals: Probe on `xlnx,axi-pcie-host-1.00.a`, bridge enable, root and downstream config reads, link-up/down logs, INTx/MSI delivery, MSI allocation/free for up to 128 vectors, controller error interrupts, and shared IRQ behavior.

# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-cpm.c

Purpose: Implements Xilinx Versal CPM/CPM5 PCIe host bridge support. It uses generic ECAM config access, CPM SLCR interrupt plumbing, controller event domains, INTx domains, bridge enablement, and variant-specific register offsets.

Important APIs/types/functions: `struct xilinx_cpm_pcie` stores bridge registers, CPM SLCR base, INTx/event domains, config window, IRQ numbers, lock, and `struct xilinx_cpm_variant`. Key functions include `xilinx_cpm_pcie_init_irq_domain()`, `xilinx_cpm_setup_irq()`, `xilinx_cpm_pcie_event_flow()`, `xilinx_cpm_pcie_intx_flow()`, `xilinx_cpm_pcie_intr_handler()`, `xilinx_cpm_pcie_parse_dt()`, `xilinx_cpm_pcie_init_port()`, and `xilinx_cpm_pcie_probe()`.

Control flow: Probe selects variant data, creates IRQ domains except for CPM5NC host, finds the bus range, maps `cpm_slcr`, creates a PCI ECAM window from `cfg`, maps `cpm_csr` for CPM5 variants, initializes bridge interrupts and bridge-enable state, maps/request event IRQs, chains INTx and the main event IRQ, assigns generic ECAM ops, and calls `pci_host_probe()`. Event flow reads IDR masked by IMR, dispatches each bit through the CPM domain, acknowledges controller and SLCR miscellaneous status, and INTx flow dispatches `IDRN` bits to the wired domain.

State and persistence: Persistent state includes interrupt masks, SLCR local interrupt enable/status, bridge-enable bit, and ECAM mapping. Driver state includes the irqdomains, chained handler bindings, raw spinlock, and variant register offsets.

Dependencies/integration: Uses Linux PCI host bridge and ECAM helpers, irqdomain/chained IRQ APIs, OF platform resources, and shared Xilinx interrupt constants. Compatible strings distinguish CPM, CPM5 host0/host1, and CPM5NC host behavior.

Risks: CPM5NC intentionally skips interrupt setup and port init, so changes must preserve this special case. Event and INTx domains share the same child interrupt-controller node but different bus tokens. Register base selection differs between CPM and CPM5. Missing cleanup of chained handlers or ECAM windows on error can leave stale IRQ plumbing.

Test signals: Boot enumeration on each compatible variant, ECAM config access, link status logs, controller error interrupt logs, INTx delivery, SLCR local interrupt acknowledgement, CPM5 host1 register offsets, CPM5NC enumeration without IRQ setup, and error-path unbind/probe retry.

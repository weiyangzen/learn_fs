# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-altera.c

## Purpose
`pcie-altera.c` is the Altera/Intel FPGA PCIe root-port host driver for multiple IP generations. It implements custom config transactions using TLP FIFOs for v1, modified packet/direct-root access for Stratix 10 v2, and direct Agilex-style root/endpoint config mechanisms for v3. It also handles INTx/AER interrupt domains and link retraining.

## Important APIs, Types, And Functions
`struct altera_pcie` stores platform data, CRA/HIP bases, IRQ, root bus number, INTx domain, bus range, and version data. Version dispatch is through `struct altera_pcie_ops` and `struct altera_pcie_data`. Config operations enter `altera_pcie_cfg_read()` / `altera_pcie_cfg_write()`, validate link/device visibility, hide root BAR0, then call `_altera_pcie_cfg_read()` / `_altera_pcie_cfg_write()`. Key helpers include `tlp_read_packet()`, `s10_tlp_read_packet()`, `get_tlp_header()`, `aglx_ep_read_cfg()`, `altera_pcie_retrain()`, and version-specific ISRs.

## Control Flow, State, And Persistence
Probe selects OF match data, maps `"Cra"` and for v2/v3 `"Hip"`, installs a chained interrupt handler, creates a four-line INTx domain, clears/enables interrupts for v1/v2 or enables CFG/AER for v3, retrains links where useful, sets host bridge sysdata/ops, and calls `pci_host_probe()`. Config reads/writes either directly access root-port config, target Agilex endpoint windows after writing `AGLX_BDF_REG`, or build config TLP headers and wait for completions. The driver updates `root_bus_nr` when software writes `PCI_PRIMARY_BUS`, so bus-number state follows PCI core changes.

## Dependencies, Integration Points, Risks, And Test Signals
The driver integrates with OF match strings for root-port 1.0, 2.0, and 3.0 F/P/R tile variants; generic PCI host bridge; irq domains; chained IRQs; and the separate Altera MSI provider. Risks include TLP completion timeouts, malformed packet handling, byte-enable/alignment errors, root bus tracking drift, and v3 CFG/AER interrupt mapping. Test root/subordinate config cycles, hidden RC BAR0, link retraining, INTx delivery, AER/CFG handling, and clean root-bus removal.

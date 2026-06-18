# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip-host.c

Purpose: Implements the Rockchip AXI PCIe root-complex driver. It parses host resources, powers regulators and PHY lanes, trains the link, programs AXI wrapper address translation, handles controller/client/legacy interrupts, supports suspend/resume, and registers a PCI host bridge.

Important APIs/types/functions: The driver uses shared `struct rockchip_pcie` and host `pci_ops` through `rockchip_pcie_ops`. Important functions include config access helpers (`rockchip_pcie_rd_own_conf()`, `rockchip_pcie_rd_other_conf()`, `rockchip_pcie_wr_conf()`), `rockchip_pcie_host_init_port()`, `rockchip_pcie_setup_irq()`, `rockchip_pcie_cfg_atu()`, `rockchip_pcie_prog_ob_atu()`, `rockchip_pcie_prog_ib_atu()`, `rockchip_pcie_suspend_noirq()`, `rockchip_pcie_resume_noirq()`, and `rockchip_pcie_probe()`.

Control flow: Probe allocates a host bridge, parses common DT plus host regulators, enables clocks and supplies, initializes resets/PHYs/link training, creates an INTx domain, programs outbound memory/I/O/message regions and inbound memory, maps the message region, requests system/client IRQs and chains legacy INTx, enables interrupts, then invokes `pci_host_probe()`. Config reads use local RC config space for the root bus and ECAM-like address offsets for downstream devices after switching the wrapper to Type 0 or Type 1 config access. Suspend sends PME_TURN_OFF, waits for L2, powers down PHY/clocks/0.9V; resume reverses setup.

State and persistence: State lives in regulator enable state, clocks, PHY lane power, `lanes_map`, IRQ domain, message region mapping, and wrapper ATU registers. The driver powers off unused lanes after link training.

Dependencies/integration: Depends on OF PCI parsing, regulator framework, GPIO PERST, PHY, reset/clock helpers from `pcie-rockchip.c`, irqdomain, chained IRQs, and Linux PCI host bridge APIs.

Risks: Sub-32-bit writes to own config space use read-modify-write and can corrupt adjacent RW1C bits. The controller supports only one device directly below the root port. ATU programming assumes memory and I/O windows exist and splits them into 1 MiB regions. Suspend depends on endpoint PME/L2 behavior and may fail if the link does not enter L2.

Test signals: RK3399 host boot enumeration, regulator and clock sequencing, Gen1/Gen2 training, lane-map debug logs, INTx delivery, controller error logs, memory/I/O BAR access, suspend/resume with endpoint traffic, and DT variants with optional 12V/3.3V supplies.

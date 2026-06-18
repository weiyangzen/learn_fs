# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-amd-mdb.c

Purpose: Implements the AMD MDB PCIe bridge host driver for `amd,versal2-mdb-host`. It wraps the DWC host core with MDB SLCR interrupt handling, event and INTx IRQ domains, reset GPIO parsing, PERST sequencing, and simple warning reports for completion/error/PM events.

Important APIs and types: `struct amd_mdb_pcie` embeds `struct dw_pcie`, maps SLCR registers, stores event and INTx IRQ domains, PERST GPIO, and INTx IRQ. Main functions are `amd_mdb_pcie_init_irq_domains()`, `amd_mdb_setup_irq()`, `amd_mdb_pcie_event()`, `amd_mdb_pcie_intr_handler()`, `dw_pcie_rp_intx()`, `amd_mdb_pcie_init_port()`, `amd_mdb_parse_pcie_port()`, `amd_mdb_add_pcie_port()`, and `amd_mdb_pcie_probe()`.

Control flow: Probe allocates the embedded DWC object, parses a child `pcie*` reset GPIO or falls back to the host node reset GPIO, maps `slcr`, creates a 32-entry MDB event domain and a four-entry wired INTx domain from the DT child interrupt-controller, disables/clears/enables all supported TLP interrupts, maps/request IRQs for named event causes, maps INTx through the event domain, requests the top-level platform IRQ as the event demux, deasserts PERST after PCIe timing delays, and enters `dw_pcie_host_init()`.

State and persistence: SLCR interrupt enable/disable/status registers retain event/INTx masks and pending bits. IRQ-domain state maps hardware causes to Linux IRQs. `pp->lock` serializes mask updates. PERST GPIO state controls endpoint reset. Generic host state lives in the embedded DWC root port.

Dependencies and integration points: Depends on OF child interrupt-controller nodes, Linux irqdomain APIs, GPIO descriptor APIs, DWC host core, and PCI timing constants. The current host ops table is empty; all platform-specific behavior is interrupt/reset setup before generic host init.

Risks: `amd_mdb_pcie_event()` demuxes every unmasked status bit, but only configured causes have installed leaf handlers; unknown bits can still hit the domain. Error events currently log warnings rather than integrating with AER. INTx status extraction relies on packed bit layout and `AMD_MDB_PCIE_INTR_INTX_ASSERT()`. Only one root port is supported despite child-node iteration. IRQ domain cleanup is manual on setup failure.

Test signals: Boot the Versal2 MDB DT, verify child or fallback reset GPIO handling, top-level interrupt demux, completion-timeout/PME/correctable/nonfatal/fatal warning logs, wired INTx delivery to PCI devices, masking/unmasking writes, host enumeration after PERST delays, and cleanup on IRQ setup failure.

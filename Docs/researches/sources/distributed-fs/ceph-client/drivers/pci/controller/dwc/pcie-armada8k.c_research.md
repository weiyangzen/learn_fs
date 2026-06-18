# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-armada8k.c

Purpose: Implements Marvell Armada-8K DWC PCIe root-complex glue. It enables clocks/PHYs, selects root-complex mode, configures AXI cache/domain attributes, enables/discards latched legacy INTx causes, controls LTSSM, and delegates host bring-up to the DWC core.

Important APIs and types: `struct armada8k_pcie` stores the DWC pointer, main and register clocks, up to four PHYs, and PHY count. Main functions are `armada8k_pcie_setup_phys()`, `armada8k_pcie_enable_phys()`, `armada8k_pcie_disable_phys()`, `armada8k_pcie_link_up()`, `armada8k_pcie_start_link()`, `armada8k_pcie_host_init()`, `armada8k_pcie_irq_handler()`, `armada8k_add_pcie_port()`, and `armada8k_pcie_probe()`.

Control flow: Probe enables the unnamed clock and optional `reg` clock, maps `ctrl` as DBI/vendor registers, discovers up to four PHYs from DT, initializes/powers them with `PHY_MODE_PCIE` and lane count, installs DWC ops, requests the controller IRQ, then calls `dw_pcie_host_init()`. Host init disables LTSSM if the link is down, writes device type as RC, sets AR/AW cache and domain attributes, and unmasks INT A-D latch bits. The IRQ handler only clears latched controller causes because endpoint/device handlers service the real interrupts.

State and persistence: Hardware state includes clock enables, PHY mode/power, global control/status, root-complex device type, AXI cache/user-domain registers, global interrupt masks, and DWC iATU/MSI/host state. Driver state tracks optional PHYs and clocks; error paths explicitly unwind PHY and clock enables.

Dependencies and integration points: Depends on DWC host core, clock and PHY frameworks, platform IRQs, OF PHY lookup, and Armada8K vendor registers at offset `0x8000`.

Risks: `armada8k_pcie_disable_phys()` iterates all four PHY slots even when some are NULL; this relies on PHY helpers tolerating NULL or can be fragile depending on API behavior. Optional old DTs without PHY handles are accepted with a warning. The controller IRQ is a latch-clear path, not a hierarchical INTx domain; changing it could duplicate device interrupt handling. AXI cache/domain defaults are platform integration sensitive.

Test signals: Boot Armada8K DTs with one/four lanes and old no-PHY bindings, verify clock and optional reg-clock handling, PHY mode lane count, RC mode register, Gen/link-up logs, legacy INTx devices still interrupt correctly while latch causes are cleared, failed host-init unwind, and DMA coherency under traffic.

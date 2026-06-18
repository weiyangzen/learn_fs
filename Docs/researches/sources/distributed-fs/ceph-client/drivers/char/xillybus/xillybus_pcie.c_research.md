<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_pcie.c -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_pcie.c

Purpose: PCIe transport wrapper for the shared Xillybus core.

Important APIs/types/functions: Matches Xillybus PCI device ID `0xebeb` for Xilinx, Altera, Actel, and Lattice vendor IDs. `xilly_probe()` initializes endpoint state, enables the PCI device, maps BAR0, enables bus mastering and MSI, requests `xillybus_isr()`, selects a DMA mask, and calls `xillybus_endpoint_discovery()`. `xilly_remove()` calls `xillybus_endpoint_remove()`.

Control flow: probe allocates a core endpoint, stores it in PCI drvdata, uses pcim-managed enable/map resources, disables L0s due to packet drop history, validates BAR0 as memory, maps BAR0, enables MSI, requests the interrupt, prefers a 32-bit DMA mask unless only 64-bit works, records DAC use, and delegates discovery. Remove delegates endpoint cleanup.

State and persistence: runtime endpoint state is stored in PCI drvdata and devres/pcim-managed resources. No persistent state.

Dependencies and integration: depends on PCI, MSI, BAR0 MMIO, DMA mask APIs, and the shared Xillybus core/class modules.

Risks: MSI enablement is mandatory and the driver does not include an INTx fallback. The 32-bit-first DMA mask choice works around old hardware but may limit DMA addressing. L0s is forcibly disabled for reliability. Endpoint cleanup must quiesce DMA before PCI-managed resources disappear.

Test signals: probe supported vendor/device IDs, verify BAR0 mapping and MSI interrupt delivery, DMA mask fallback on 32-bit/64-bit platforms, stream discovery and I/O, link power-management behavior, remove/unbind with active channels, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_pcie.c -->

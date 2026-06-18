# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/hwif.c

Purpose: Selects and initializes the hardware-interface callback tables for every supported stmmac core family. It maps core type, Synopsys version, and XGMAC device ID to descriptor, DMA, MAC, PTP, TC, MMC, EST, VLAN, mode, FPE register offsets, and setup functions.

Important APIs and flow: `stmmac_hwif_init()` reads the version register, saves `priv->synopsys_id`, allocates `mac_device_info`, honors platform `mac_setup` overrides, finds the best `stmmac_hwif_entry`, fills missing callback pointers, sets `ptpaddr`, `mmcaddr`, `estaddr`, copies PTP clock ops, runs setup, and stores quirk callbacks. `stmmac_reset()` dispatches either platform reset or DMA reset. Internal quirk helpers choose normal/enhanced descriptors and ring/chain mode for older cores.

Control flow and state: The static `stmmac_hw[]` table is ordered so newer versions override older entries by reverse search. State persists in `priv->hw`, `priv->synopsys_id`, FPE register config, and subsystem MMIO base pointers. Platform overrides can partially prefill the MAC structure before generic fallback fills gaps.

Dependencies and integration: Includes all relevant stmmac operation providers: DWMAC100/1000/4/5, XGMAC2, VLAN, PTP, EST, FPE, descriptors, DMA, MMC, and TC. It is the main bridge between probe-time platform data and runtime callback dispatch in `hwif.h`.

Risks and test signals: Table ordering and version matching decide the whole driver personality. Test each core type, custom `mac_setup`, zero version register, XGMAC device ID mismatch, GMAC 3.50 extended descriptor threshold, ring/chain mode selection, FPE offset assignment, and failure paths for missing table entries.

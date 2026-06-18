<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmmac.h -->
# sources/distributed-fs/ceph-client/include/linux/stmmac.h

Purpose: Defines platform data for the Synopsys/STMicroelectronics stmmac Ethernet driver, including DMA, AXI, queue, safety, core type, clocks, PHY/PCS, callbacks, flags, and SoC glue hooks.

Important APIs/types/functions: queue limits, RX checksum constants, CSR clock divisors, MTL algorithm and queue mode constants, DMA burst constants, `struct stmmac_mdio_bus_data`, `struct stmmac_dma_cfg`, `struct stmmac_axi`, `struct stmmac_rxq_cfg`, `struct stmmac_txq_cfg`, `struct stmmac_safety_feature_cfg`, `struct dwmac4_addrs`, `enum dwmac_core_type`, `STMMAC_FLAG_*`, and `struct plat_stmmacenet_data`.

Control flow: Platform or device-tree glue populates `plat_stmmacenet_data` before the stmmac core probes. The driver consumes PHY interface, queue counts/config, DMA/AXI parameters, clock/reset handles, callbacks for SoC-specific setup, MAC/PCS/SerDes hooks, timestamp configuration, and interrupt vector assignments.

State and persistence behavior: This is configuration state passed into the network driver. It persists for the lifetime of the platform device and points to clocks, resets, node references, queue arrays, callback private data, and embedded fallback DMA config.

Dependencies: Platform device support, phylink, clocks, reset controls, net device types, PTP/system counter types, and stmmac core internals.

Integration points: Platform Ethernet glue, phylink/PCS/PHY, MDIO, DMA/AXI, PTP timestamping, MSI routing, safety features, clock/reset management, and SoC-specific MAC setup.

Risks: Incorrect queue counts beyond `MTL_MAX_*`, mismatched PHY interface/clock callbacks, wrong DMA burst settings, or invalid clock/reset pointers can prevent link bring-up or corrupt DMA. Callback lifetimes must match `bsp_priv` and device lifetime.

Test signals: stmmac probe on representative platforms, phylink mode matrix, MDIO clock divider tests, multi-queue traffic tests, DMA burst/performance tests, suspend/resume, PTP timestamp tests, and safety interrupt injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmmac.h -->

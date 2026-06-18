# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac.h

Purpose: Defines the register layout, descriptor format, feature flags, shared state, and exported API contract for the Broadcom GMAC driver family. It lets BCMA and platform front-ends plug into the shared `bgmac.c` core.

Important APIs/types: Register constants cover device control/status, interrupts, PHY access, DMA engines, MIB counters, UniMAC base, BCMA IOCTL/IOST, chipcontrol interface types, and descriptor control bits. `struct bgmac_dma_desc` is the 64-bit DMA descriptor; `struct bgmac_dma_ring` tracks descriptor memory, MMIO base, unaligned index base, and slots. `struct bgmac` stores bus-specific unions, device pointers, netdev/NAPI, mdiobus, DMA rings, stats, IRQ state, link state, PHY address, feature flags, and callback pointers. Exported functions are shared lifecycle/PHY helpers.

Control flow support: Inline wrappers dispatch register, IDM, clock, chipcommon, bus-clock, common-core, and PHY connection operations through front-end callbacks. This separates bus mechanics from shared MAC/DMA logic.

State/persistence: The header defines one persistent per-device `struct bgmac`. DMA ring slots carry either SKBs or RX buffers plus DMA addresses. Feature flags persist from probe and gate reset/init behavior. MIB arrays can store counter snapshots, though stats update is mostly direct reads in the implementation.

Dependencies/integration: Includes netdevice and local `unimac.h`; uses BCMA constants from included build context and phylib types through consumers. Front-ends must initialize all callback pointers before `bgmac_enet_probe()`.

Risks/test signals: Callback-pointer completeness and feature flag correctness are critical. Changes to descriptor constants affect RX/TX hardware directly. Validate compile coverage for BCMA and platform builds, 32/64-bit DMA addresses, fixed PHY and MDIO PHY, ethtool stats size/order, and all feature-flag combinations.

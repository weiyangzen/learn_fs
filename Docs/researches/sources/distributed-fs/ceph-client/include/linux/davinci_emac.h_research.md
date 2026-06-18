# sources/distributed-fs/ceph-client/include/linux/davinci_emac.h

Purpose: Provides legacy platform-data structures for TI DaVinci EMAC and MDIO devices.

Important APIs, types, and functions: Defines `struct mdio_platform_data` with `bus_freq`, `struct emac_platform_data` with MAC address, control/RAM offsets, hardware RAM address/size, PHY selector, RMII/version flags, no-BD-RAM flag, and board interrupt enable/disable callbacks. Version constants distinguish DM644x (`EMAC_VERSION_1`) and DM646x (`EMAC_VERSION_2`).

Control flow: Board or platform setup code populates these structures before registering EMAC/MDIO platform devices. The network driver later reads the fields to select PHY behavior, register layout, memory placement, and interrupt handling callbacks.

State and persistence: The structures describe static board state. Runtime link state, DMA rings, statistics, and PHY state are owned by the EMAC/MDIO drivers.

Dependencies and integration points: Depends on Ethernet address sizing and NVMEM consumer infrastructure. Integrates with platform-device registration, PHY/MDIO selection, SoC control-module addressing, and board-specific interrupt glue.

Risks and test signals: Risks include malformed `phy_id` strings, wrong register offsets for the SoC version, invalid MAC addresses, and callback lifetime bugs. Test board boot, PHY auto-selection and fixed 100/full mode, RMII mode, interrupt masking/unmasking, and MAC address sourcing.

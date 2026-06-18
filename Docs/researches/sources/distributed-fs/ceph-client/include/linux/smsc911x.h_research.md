# sources/distributed-fs/ceph-client/include/linux/smsc911x.h

Purpose: This header defines the platform-data contract for the SMSC LAN911x/LAN921x Ethernet controller driver. It is used by non-DT or board-file style platform devices to describe interrupt wiring, bus width, PHY selection, and an optional fixed MAC address.

Important APIs/types/functions: The only exported type is `struct smsc911x_platform_config`, with `irq_polarity`, `irq_type`, `flags`, `shift`, `phy_interface`, and `mac[ETH_ALEN]`. Constants define active-low/high IRQ polarity, open-drain/push-pull IRQ type, 16-bit/32-bit access flags, internal/external PHY forcing, MAC-address preservation, and `SMSC911X_SWAP_FIFO`.

Control flow: There is no executable flow in the header. The network driver reads the struct during platform-device probe, then chooses register access width, IRQ configuration, PHY binding, and FIFO byte-swapping behavior.

State and persistence: Configuration is static platform state attached to `dev.platform_data`. The MAC address field may seed persistent network identity if `SMSC911X_SAVE_MAC_ADDRESS` is selected.

Dependencies and integration: Depends on `linux/phy.h` for `phy_interface_t` and `linux/if_ether.h` for `ETH_ALEN`. Integrates with platform bus Ethernet devices and PHYLIB.

Risks and test signals: Mis-set bus width, shift, FIFO byte-swap, or PHY flags can produce silent packet corruption or probe failure. Useful tests are platform probe, PHY attach, IRQ delivery, link up/down, and traffic on big-endian or board-file systems.

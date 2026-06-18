# sources/distributed-fs/ceph-client/include/linux/smscphy.h

Purpose: This header centralizes SMSC/Microchip Ethernet PHY register definitions and shared helper prototypes for LAN83C185/LAN87xx PHY drivers, including interrupts, energy detect, and wake-on-LAN programming.

Important APIs/types/functions: It names MII registers such as `MII_LAN83C185_ISF`, `IM`, `CTRL_STATUS`, and `SPECIAL_MODES`; interrupt bits for link down, auto-negotiation complete, and energy-on; power and mode masks; and LAN874x MMD wake filters, PME, magic packet, broadcast, and pattern-detect bits. It declares `smsc_phy_config_intr`, `smsc_phy_handle_interrupt`, `smsc_phy_config_init`, `lan87xx_read_status`, tunable get/set helpers, and `smsc_phy_probe`.

Control flow: PHY drivers include this header to implement probe/config/init, configure interrupt masks, service PHY interrupt status, read link state, and expose ethtool tunables.

State and persistence: State lives in PHY registers and MMD WOL registers. WOL filters and PME state can persist across suspend depending on PHY power mode.

Dependencies and integration: The prototypes consume `struct phy_device`, `irqreturn_t`, and `struct ethtool_tunable`, tying the header to PHYLIB, IRQ handling, and ethtool.

Risks and test signals: Incorrect interrupt masks can miss link changes or storm interrupts. WOL bit placement is hardware-sensitive. Test with PHY interrupt mode, polling fallback, link renegotiation, suspend/resume WOL, and ethtool tunable reads/writes.

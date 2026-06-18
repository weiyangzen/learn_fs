# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_enet.h

**Purpose:** Defines BCM63xx Ethernet MAC and Ethernet switch platform data plus ENET DMA channel register indexing.

**Important APIs/types/functions:** Exports `struct bcm63xx_enet_platform_data` with MAC, PHY presence/internal/external info, PHY IRQ, pause/forced link settings, optional MII config callback, DMA masks, SRAM flag, channel width/descriptor shift, and RX/TX channels. Defines switch constants `ENETSW_MAX_PORT`, `ENETSW_PORTS_6328`, `ENETSW_PORTS_6368`, `ENETSW_RGMII_PORT0`, `struct bcm63xx_enetsw_port`, `struct bcm63xx_enetsw_platform_data`, registration functions `bcm63xx_enet_register()` and `bcm63xx_enetsw_register()`, `enum bcm63xx_regs_enetdmac`, and inline `bcm63xx_enetdmacreg()`.

**Control flow:** Board setup fills MAC/PHY/switch/DMA data, registers either legacy MAC units or integrated switch devices, and the network driver configures PHY or forced link state, DMA channels, and MII callbacks from that data.

**State and persistence behavior:** Platform data persists as device registration configuration. DMA register offset table is extern state selected by CPU code. Network runtime state is held by drivers, not this header.

**Dependencies and integration points:** Depends on Ethernet address types, `bcm63xx_regs.h`, net_device callback signatures, BCM63xx CPU/resource tables, PHY/MII core, and IUDMA descriptors.

**Risks:** Misconfigured PHY and DMA masks can prevent link or DMA traffic. Callback prototypes couple board code to driver MII semantics. Switch port arrays must match real port count and RGMII wiring.

**Test signals:** Boot MAC and switch variants, verify MAC address, PHY attach/interrupt, pause and forced-link modes, RX/TX DMA interrupts, integrated SRAM behavior, all switch ports, and register offset selection.

# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_eth.h

**Purpose:** Defines platform-specific Ethernet configuration for Au1x00 MAC drivers.

**Important APIs/types/functions:** Exports `struct au1000_eth_platform_data` with PHY static/search flags, PHY address, bus ID, PHY IRQ, and 6-byte MAC address. Declares `au1xxx_override_eth_cfg(unsigned port, struct au1000_eth_platform_data *eth_data)`.

**Control flow:** Board code can override per-port Ethernet configuration before MAC driver registration. The driver then uses PHY search/static settings, interrupt routing, and MAC address data to attach PHYs and configure networking.

**State and persistence behavior:** No local state in the header. The override function implementation mutates platform Ethernet configuration; MAC addresses and PHY config persist as device registration data.

**Dependencies and integration points:** Integrated by Alchemy board setup, Ethernet MAC driver, MII/PHY layer, and NVRAM/bootloader MAC address sources.

**Risks:** Wrong PHY address/search policy can bind the wrong PHY or fail link. Invalid MAC addresses create duplicate network identities. Board overrides need to occur before device registration.

**Test signals:** Boot each board, verify MAC addresses, PHY attachment, link negotiation, PHY IRQ delivery, dual-MAC configurations, and fallback behavior when PHY search flags differ.

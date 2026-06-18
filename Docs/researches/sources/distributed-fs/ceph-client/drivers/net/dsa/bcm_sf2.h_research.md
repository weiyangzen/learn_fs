# sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2.h

Purpose: this header defines the private Broadcom Starfighter 2 switch contract shared by the main SF2 driver and the CFP classifier. It describes hardware parameters, per-port status, classifier state, register access helpers, interrupt mask helpers, and CFP entry points exported to DSA ethtool hooks.

Important APIs, types, and functions: `struct bcm_sf2_hw_params` stores detected top/core/GPHY revisions and port/resource counts. `struct bcm_sf2_port_status` caches PHY interface, link, and enabled state. `struct bcm_sf2_cfp_priv` owns the classifier lock, used and unique rule bitmaps, rule count, and rule list. `struct bcm_sf2_priv` is the central driver state, including MMIO bases, reset/clock handles, b53 device, IRQ masks, MDIO buses, masks for internal PHYs, Broadcom tags and WoL, and CFP state. Inline helpers include `bcm_sf2_to_priv()`, `bcm_sf2_mangle_addr()`, `core_readl()/core_writel()`, `reg_readl()/reg_writel()`, generated `*_readl()` helpers, 64-bit latched accessors, and `intrl2_*_mask_set/clear()`.

Control flow: C files include this header to translate DSA switch pointers to SF2 state, read and write the switch core and ancillary register windows, protect latched 64-bit accesses with `indir_lock`, and maintain software interrupt-mask shadows while programming INTRL2 mask registers. The prototypes at the bottom connect `bcm_sf2.c` ethtool callbacks to `bcm_sf2_cfp.c`.

State and persistence: the header itself stores no state, but it defines the fields that persist across runtime operations and resume replay. Important shadow state includes register offset tables, core register alignment, IRQ masks, port status, MDIO routing masks, WoL mask, and CFP rule bitmaps/list.

Dependencies and integration points: it depends on platform devices, I/O accessors, locks, MII, ethtool, VLAN definitions, reset controls, DSA, `bcm_sf2_regs.h`, and b53 private definitions. It is the local ABI between the SF2 bus glue, b53 switch core, and CFP support.

Risks: the generated 64-bit accessors rely on REG_DIR_DATA_READ/WRITE latching and only provide relative atomicity through `indir_lock`. Interrupt mask helpers update software shadows and hardware masks in a specific order. `reg_readl()` uses compatible-provided offset tables; missing offsets silently become offset zero if the table is incomplete.

Test signals: compile coverage of both SF2 C files, 32/64-bit MIB access correctness, interrupt mask shadow consistency, CFP lock/list initialization, and valid register offset tables for every compatible.

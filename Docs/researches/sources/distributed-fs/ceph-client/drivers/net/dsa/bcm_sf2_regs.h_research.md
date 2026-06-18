# sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2_regs.h

Purpose: this header defines the Broadcom Starfighter 2 register IDs, offsets, bit fields, and resource constants used by the SF2 platform driver and CFP classifier. It covers the register indirection table, switch control/status, GPHY control, crossbar selection, LEDs, RGMII controls, interrupt banks, ACB queues, core forwarding and port state, VLAN/FDB/MIB-related core registers, CFP TCAM/action/rate/stat RAM, UDF layout registers, and global resource sizes.

Important APIs, types, and functions: `enum bcm_sf2_reg_offs` names logical offsets in the `reg_offsets` tables. Macros such as `MDIO_MASTER_SEL`, `PHY_RESET`, `RGMII_MODE_EN`, `P_IRQ_MASK()`, `ACB_QUEUE_CFG()`, `CORE_G_PCTL_PORT()`, `CORE_STS_OVERRIDE_GMIIP_PORT()`, `CORE_PORT_TC2_QOS_MAP_PORT()`, `CORE_CFP_DATA_PORT()`, `CORE_CFP_MASK_PORT()`, and CFP action/rate/stat bits are consumed directly by the C files. Constants define `UDF_NUM_SLICES`, `UDFS_PER_SLICE`, `CFP_NUM_RULES`, and `SF2_NUM_EGRESS_QUEUES`.

Control flow: the main driver uses these definitions to reset the switch, power ports and GPHYs, program IMP forwarding, configure traffic class to queue mapping, set link overrides, configure ACB thresholds, process interrupts, and expose b53 core access. The CFP driver uses the TCAM access register, data/mask ports, UDF offsets, action policy fields, policer disable mode, and statistic RAM selectors to create hardware flow rules.

State and persistence: the header documents persistent hardware state rather than storing it. Relevant state includes switch control and revision registers, port memory power state, link/speed/duplex overrides, LED control policy, interrupt mask/status, ACB thresholds, VLAN table entries, CFP table contents, UDF configuration, and per-rule counters.

Dependencies and integration points: it is included by `bcm_sf2.h`, `bcm_sf2.c`, and `bcm_sf2_cfp.c`. The logical `REG_*` enum is tied to the compatible-specific offset arrays in `bcm_sf2.c`.

Risks: bitfield definitions are hardware ABI. Typographical or shift/mask mistakes directly corrupt MMIO programming. Some macros encode SoC-specific alternate layouts, such as `CORE_STS_OVERRIDE_IMP2` and BCM4908 crossbar fields. The register enum must remain synchronized with all offset arrays.

Test signals: compile-time use across SF2 files, probe and register dump sanity on each compatible, interrupt status/mask correctness, ACB threshold programming, link override behavior, CFP TCAM programming and counters, and LED/GPHY/RGMII control writes matching hardware documentation.

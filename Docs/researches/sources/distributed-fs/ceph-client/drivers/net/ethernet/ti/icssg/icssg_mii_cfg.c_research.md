<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_cfg.c

## Purpose

`icssg_mii_cfg.c` is a small register helper layer for ICSSG MII-RT and MII-G-RT configuration. It updates inter-packet gap, MTU frame bounds, RGMII speed/duplex/in-band bits, interface mode selection, and reads RGMII status bitfields.

## Important APIs, Types, and Functions

Exported functions are `icssg_mii_update_ipg()`, `icssg_mii_update_mtu()`, `icssg_update_rgmii_cfg()`, `icssg_miig_set_interface_mode()`, `icssg_rgmii_cfg_get_bitfield()`, `icssg_rgmii_get_speed()`, and `icssg_rgmii_get_fullduplex()`.

## Control Flow

Callers pass a regmap, slice/MII number, and link parameters. IPG writes go to `PRUSS_MII_RT_TX_IPG0/1`, with MII1 preserving TX_IPG0 around the write. MTU updates add Ethernet header and FCS before programming RX frame max fields. RGMII config computes slice-specific masks and sets gigabit, in-band 10M RGMII, and full-duplex bits. Interface mode writes MII or RGMII mode fields in `ICSSG_CFG_OFFSET`.

## State and Persistence Behavior

All state is hardware register state in MII-RT or MII-G-RT regmaps. The helpers do not store software state; they reflect values from `struct prueth_emac` and are called during configuration and link adjustment.

## Dependencies and Integration Points

It depends on `icssg_mii_rt.h` register definitions, PHY interface helpers, `prueth_emac_slice()`, `regmap`, and Ethernet constants. Main users are `icssg_config.c`, `icssg_prueth.c`, `icssg_prueth_sr1.c`, and SR1 speed command construction.

## Risks and Edge Cases

The MII1 IPG path temporarily reads and rewrites TX_IPG0, implying hardware side effects or ordering constraints that should not be simplified without datasheet confirmation. MTU programming assumes callers already validate netdev MTU limits. RGMII in-band enable is only set for 10M RGMII, matching driver workaround behavior.

## Test Signals

Validate register writes during link transitions for MII and RGMII, 10/100/1000 speeds, full/half duplex, and MTU changes. SR1 tests should confirm speed/duplex readback used for firmware commands matches `RGMII_CFG` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_cfg.c -->

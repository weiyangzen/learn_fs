<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_rt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_rt.h

## Purpose

`icssg_mii_rt.h` defines MII-RT and MII-G-RT register offsets, bit masks, speed encodings, interface mode encodings, and helper prototypes for ICSSG MII/RGMII programming.

## Important APIs, Types, and Functions

The file defines `PRUSS_MII_RT_*` offsets for RX/TX config, CRC, IPG, parser status, frame size, preamble count, and error registers; `ICSSG_CFG_*` and `RGMII_CFG_*` masks; `enum mii_mode`; `ICSS_MII0/ICSS_MII1`; and prototypes implemented in `icssg_mii_cfg.c`.

## Control Flow

There is no runtime flow. These definitions are consumed by configuration and link-adjustment code to build `regmap_update_bits()` operations and decode RGMII speed/full-duplex state.

## State and Persistence Behavior

The constants describe persistent hardware register state, not software state. Values written through these masks remain in the ICSSG hardware until reconfigured, reset, or power-cycled.

## Dependencies and Integration Points

The header includes Linux Ethernet and PHY definitions and forward declares `struct regmap` and `struct prueth_emac`. It is included by MII config, general config, SR1, and main PRU Ethernet driver files.

## Risks and Edge Cases

Bit definitions are hardware ABI. Incorrect masks or shifts can break link mode, frame sizing, TX mux selection, and speed/duplex reporting. `PRUSS_MII_RT_RX_FRMS_MAX_FRM_LRE` references `ICSS_LRE_TAG_RCT_SIZE`, so include ordering must provide that macro where LRE max-frame support is used.

## Test Signals

Build coverage catches missing macro dependencies. Runtime signals include successful MII/RGMII link up at supported speeds, correct MTU enforcement, no RX frame-size errors after MTU changes, and expected speed/full-duplex readback in SR1 speed command paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_mii_rt.h -->

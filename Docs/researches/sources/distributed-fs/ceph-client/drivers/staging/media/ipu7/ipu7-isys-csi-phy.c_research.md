# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi-phy.c

## Purpose

This file programs the IPU7/IPU8 CSI-2 DWC controller and C/D-PHY register blocks for camera sensor links, including reset, data-ID filters, DPHY/CPHY tuning tables, lane aggregation, readiness polling, and powerdown.

## Important APIs, Types, and Functions

Public APIs are `ipu7_isys_csi_phy_powerup()` and `ipu7_isys_csi_phy_powerdown()`. Internal helpers read/write PHY, CSI, and GPREG registers; apply bit masks; configure CSI controller interrupts/lanes/mode; reset PHY; configure data IDs from remote subdev frame descriptors; poll PHY readiness; calculate table-driven DPHY/CPHY parameters; and configure a PHY based on link frequency, lane count, mode, and aggregation.

## Control Flow

Powerup remaps non-IPU7 port-A links with more than two lanes into aggregation mode, resets the primary PHY, programs lane force/control and mode, optionally resets/programs port B for aggregation, configures the CSI controller and data ID monitors, configures DPHY or CPHY from remote link frequency, releases reset/shutdown, waits for ready, clears force controls, and repeats configuration/readiness for port B in aggregation mode. Powerdown resets the active port and also port B when aggregation was used.

## State and Persistence Behavior

Register programming persists in ISYS MMIO/PHY hardware until reset or powerdown. A static bitmap `data_ids` tracks use of eight DWC data-ID monitor slots, and `isys->phy_rext_cal` caches calibration from PHY0 for reuse on other PHYs.

## Dependencies and Integration Points

It depends on media controller remote-pad lookup, V4L2 subdev frame descriptors, CSI2 register definitions, platform register bases, IPU hardware-version helpers, and CSI2 link-frequency helpers.

## Risks and Edge Cases

The global `data_ids` bitmap is not keyed per controller and is not cleared in this file on powerdown, so repeated configurations may exhaust monitors unless reset elsewhere. Link frequency lookup failure aborts PHY config. Hardware-generation and port-specific lane mappings are subtle. Many tuning writes are table-driven and sensitive to mbps range boundaries.

## Test Signals

Exercise DPHY and CPHY links, 1/2/4 lane modes, IPU7 vs IPU7.5/IPU8 variants, port-A aggregation, multiple VCs/data types, repeated stream start/stop, link-frequency failure handling, PHY ready timeout, and sensor frame descriptor validation.

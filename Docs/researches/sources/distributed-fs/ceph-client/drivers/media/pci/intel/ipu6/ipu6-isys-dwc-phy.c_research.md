# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-dwc-phy.c

## Purpose
This file implements the Synopsys DWC D-PHY power/configuration path for IPU6 CSI-2 receivers. It programs DPHY MMIO and test-interface registers, selects frequency ranges from sensor link rate, supports two-PHY aggregation for 4-lane ports, handles termination calibration reuse, and powers PHYs up/down for CSI-2 streaming.

## Important APIs, types, and functions
Low-level helpers include `dwc_dphy_read/write()`, mask variants, test-interface read/write helpers, `dwc_dphy_pwr_up()`, and `ipu6_isys_dwc_phy_reset()`. `freqranges[]` maps Mbps ranges to `hsfreq`, default Mbps, and DDL oscillator targets. `ipu6_isys_dwc_phy_config()` programs HSFREQRANGE, optional forced term calibration, DDL target, deskew polarity, CFGCLKFREQRANGE from buttress ref clock, and DFT controls. `ipu6_isys_dwc_phy_aggr_setup()` configures master/slave aggregated PHY clocking. Public entry point `ipu6_isys_dwc_phy_set_power()` validates port/lane, calculates Mbps, and powers the right PHY or PHY pair.

## Control flow and integration points
CSI-2 stream enable calls this via `isys->phy_set_power()`. The function reads link frequency from the matching CSI-2 subdevice, converts to Mbps, resets PHYs, configures one PHY for 1/2-lane mode or primary/secondary PHYs for 4-lane aggregation, and polls for idle/ULP readiness. Stream disable resets the relevant PHYs.

## State, persistence, and dependencies
Most state is hardware register state. `isys->phy_termcal_val` persists a term-calibration value learned from PHY E and reused later. Dependencies include ISYS platform base/register offsets, CSI-2 link-frequency helper, buttress reference clock, bitfield helpers, delays, and poll timeouts.

## Risks and test signals
Risks are unsupported link rates, bad frequency table selection, 4-lane aggregation on odd ports, test-interface timeout, stale termcal override, incorrect ref-clock calculation, and PHY not reaching idle/ULP. Test signals include successful streaming at multiple link frequencies, 1/2/4-lane configurations, aggregation on valid ports only, no DWC IFC timeout logs, stable repeated stream toggles, and CSI receiver error-free capture.

# sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-lib.h

## Purpose
Declares the shared Broadcom PHY helper interface and 28 nm misc register tuple macros consumed by Broadcom PHY drivers.

## Important APIs, Types, and Functions
Defines `MISC_ADDR` and AFE/PLL/DSP register tuples such as `DSP_TAP10`, `PLL_PLLCTRL_1`, `AFE_RXCONFIG_0`, and `AFE_TX_CONFIG`. Declares expansion, auxctl, misc, shadow, and RDB accessors; interrupt helpers; APD, EEE, downshift, stats, calibration, jumbo, cable-test, optional PTP, WOL, LED brightness, and LRE autoneg functions. Inline helpers `bcm_phy_write_exp_sel` and `bcm_phy_read_exp_sel` add the expansion select bit.

## Control Flow and State
This header has no runtime control flow except optional PTP stubs selected by `CONFIG_BCM_NET_PHYPTP`. It defines API contracts for callers to provide stats shadow storage and to choose locked or unlocked register access variants.

## Dependencies and Integration Points
Includes `linux/brcmphy.h`, `linux/phy.h`, and `linux/interrupt.h`, forward-declares `struct ethtool_wolinfo`, and is included by Broadcom PHY drivers that share common register sequences. The PTP section bridges to `bcm-phy-ptp` when enabled while allowing non-PTP builds to compile.

## Risks and Test Signals
Risks include prototype drift with `bcm-phy-lib.c`, incorrect use of unlocked `__bcm_*` helpers outside an MDIO bus lock, PTP stub mismatch, and tuple macro arguments being misread as single register constants. Test signals are all Broadcom PHY driver builds, PTP-enabled and disabled builds, sparse/prototype checks, and runtime tests that exercise each exported helper from at least one consumer.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_cfg.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_cfg.h` declares RTL8723B-specific PHY register access, MAC/BB/RF configuration, transmit-power calculation, channel switching, and bandwidth mode operations. The source was reviewed as a complete 63-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `PHY_QueryBBReg_8723B`, `PHY_SetBBReg_8723B`, `PHY_QueryRFReg_8723B`, `PHY_SetRFReg_8723B`, `PHY_BBConfig8723B`, `PHY_RFConfig8723B`, `PHY_MACConfig8723B`, `PHY_SetTxPowerIndex`, `PHY_GetTxPowerIndex`, `PHY_SetTxPowerLevel8723B`, `PHY_SwChnl8723B`, and `PHY_SetSwChnlBWMode8723B`.

## Control Flow

Initialization calls MAC, BB, and RF config routines; later MLME or regulatory changes call channel/bandwidth and power-index helpers that program BB/RF registers through masked read-modify-write accessors.

## State and Persistence Behavior

The persistent effects are hardware register values and HAL transmit-power tables derived from efuse, bandwidth, channel, and rate.

## Dependencies and Integration Points

Depends on `struct adapter`, `enum channel_width`, register bit helpers, efuse power info, and the 8723B PHY implementation. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Masked register writes are fragile; wrong masks or channel inputs can violate regulatory power limits or destabilize RF calibration. Loop and stall constants bound hardware polling behavior.

## Test Signals

PHY config success/failure checks, per-channel TX power validation, bandwidth transition tests, and BB/RF register trace diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_cfg.h -->

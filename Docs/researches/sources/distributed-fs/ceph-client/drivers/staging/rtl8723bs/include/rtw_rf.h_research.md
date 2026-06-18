<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_rf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_rf.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_rf.h` defines RF/channel constants, regulatory classes, channel widths, extension channel offsets, and wireless mode masks for the 2.4 GHz RTL8723BS device. The source was reviewed as a complete 100-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct regulatory_class`, `enum channel_width`, `enum extchnl_offset`, `MAX_CHANNEL_NUM_2G`, `NUM_REGULATORYS`, `HAL_PRIME_CHNL_OFFSET_*`, wireless mode constants, and rate/channel helper declarations.

## Control Flow

MLME channel planning, PHY channel switching, cfg80211 regulatory setup, and rate/bandwidth negotiation use these constants.

## State and Persistence Behavior

No storage here; adapter/HAL/MLME structs store selected channel, bandwidth, offset, and regulatory plan.

## Dependencies and Integration Points

Used by `hal_phy_cfg.h`, `rtw_mlme_ext.h`, `rtw_cmd.h`, `rtw_xmit.h`, and cfg80211 regulatory code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Regulatory and bandwidth constants must be correct for 2.4 GHz-only hardware. Channel width mismatch affects PHY register programming and advertised capabilities.

## Test Signals

Channel plan validation, cfg80211 regulatory domain smoke, 20/40 MHz association, and channel switch operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_rf.h -->

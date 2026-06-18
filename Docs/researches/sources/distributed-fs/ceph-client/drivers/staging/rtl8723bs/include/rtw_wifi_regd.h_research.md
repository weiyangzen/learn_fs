<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_wifi_regd.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_wifi_regd.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_wifi_regd.h` declares cfg80211 regulatory helper initialization for the Realtek driver. The source was reviewed as a complete 17-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtw_regd_init`.

## Control Flow

Wiphy setup calls `rtw_regd_init` to attach regulatory behavior based on adapter/eeprom channel plan before userspace uses cfg80211.

## State and Persistence Behavior

Regulatory state is stored in cfg80211/wiphy and adapter channel-plan fields.

## Dependencies and Integration Points

Depends on cfg80211 setup, `rtw_eeprom.h` channel plan, and `rtw_rf.h` channel constants. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Incorrect regulatory initialization can advertise disallowed channels or block valid ones.

## Test Signals

iw regulatory output, channel list validation by country/domain, and scan availability across channel plans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_wifi_regd.h -->

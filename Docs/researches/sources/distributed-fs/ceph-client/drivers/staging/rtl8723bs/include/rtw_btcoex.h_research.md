<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_btcoex.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_btcoex.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_btcoex.h` declares Bluetooth coexistence hooks for binding adapter state, initialization, IPS/LPS notifications, scan/connect/media status notifications, and display/debug helpers. The source was reviewed as a complete 28-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtw_btcoex_Initialize`, `rtw_btcoex_PowerOnSetting`, `rtw_btcoex_InitHwConfig`, `rtw_btcoex_IpsNotify`, `rtw_btcoex_LpsNotify`, `rtw_btcoex_ScanNotify`, `rtw_btcoex_ConnectNotify`, `rtw_btcoex_MediaStatusNotify`, and `rtw_btcoex_HaltNotify`.

## Control Flow

Power, scan, association, and link-state paths notify the coexistence module so firmware/HAL policy can adjust RF sharing between Wi-Fi and Bluetooth.

## State and Persistence Behavior

Updates coexistence private state, firmware coexistence commands, and possibly antenna/RF scheduling settings.

## Dependencies and Integration Points

Used by HAL, MLME, power-control, and RTL8723B command code; depends on adapter/HAL coexistence data. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Notification order matters around power transitions. Missing notifications can cause poor Wi-Fi or BT throughput and connection instability.

## Test Signals

Wi-Fi scan/connect while BT active, IPS/LPS transitions with BT, coexistence debug output, and throughput coexistence smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_btcoex.h -->

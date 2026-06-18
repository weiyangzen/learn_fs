<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_cmd.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_cmd.h` defines RTL8723B firmware H2C command IDs, power-mode parameter structs, reserved-page layout, Bluetooth coexistence commands, and firmware media/status helpers. The source was reviewed as a complete 182-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `enum h2c_cmd_8723B`, `struct cmd_msg_parm`, `struct setpwrmode_parm`, `struct H2C_8723B_BTMP_OPER`, `struct RSVDPAGE_LOC`, `rtl8723b_set_FwPwrMode_cmd`, `rtl8723b_set_FwJoinBssRpt_cmd`, `rtl8723b_set_rssi_cmd`, `rtl8723b_Add_RateATid`, `rtl8723b_set_FwMediaStatusRpt_cmd`, and reserved-page download helpers.

## Control Flow

MLME, power-control, rate-adaptation, and BT coexistence paths package small H2C messages and send them through the HAL command mailbox to firmware.

## State and Persistence Behavior

Firmware-visible state includes power mode, join status, reserved-page addresses, RSSI/rate masks, media status, and BT MP operation state.

## Dependencies and Integration Points

Depends on `rtw_cmd.h`, `hal_intf.h`, power control state, firmware download code, and reserved-page beacon construction. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

H2C payload length and field layout must match firmware. Reserved-page offsets are easy to corrupt and can break PS-Poll, null data, or WoWLAN-like firmware behavior.

## Test Signals

Trace H2C bytes, connect/disconnect, LPS transitions, reserved-page download, rate mask updates, and BT coexistence command smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_cmd.h -->

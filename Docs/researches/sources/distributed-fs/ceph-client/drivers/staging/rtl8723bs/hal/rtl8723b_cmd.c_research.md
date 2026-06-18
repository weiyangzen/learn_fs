# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_cmd.c

## Purpose

`rtl8723b_cmd.c` constructs and sends RTL8723B firmware H2C commands, builds reserved-page management frames used by firmware power save and BT coexistence, downloads those pages into TX packet buffer, and configures rate adaptation, RSSI reporting, media status, and power modes. The source was read as a complete 963-line file.

## Important APIs, Types, and Functions

Important functions include `FillH2CCmd8723B`, `rtl8723b_set_FwMediaStatusRpt_cmd`, `rtl8723b_set_FwMacIdConfig_cmd`, `rtl8723b_set_rssi_cmd`, `rtl8723b_set_FwPwrMode_cmd`, `rtl8723b_set_FwPsTuneParam_cmd`, `rtl8723b_set_FwPwrModeInIPS_cmd`, `rtl8723b_download_rsvd_page`, `rtl8723b_set_FwJoinBssRpt_cmd`, `rtl8723b_Add_RateATid`, and `rtl8723b_download_BTCoex_AP_mode_rsvd_page`. Internal builders include `_is_fw_read_cmd_down`, `ConstructBeacon`, `ConstructPSPoll`, `ConstructNullFunctionData`, `rtl8723b_set_FwRsvdPage_cmd`, `rtl8723b_set_FwRsvdPagePkt`, `ConstructBtNullFunctionData`, and `SetFwRsvdPagePkt_BTCoex`.

## Control Flow

`FillH2CCmd8723B` serializes H2C mailbox access with `h2c_fwcmd_mutex`, waits for firmware to clear the selected mailbox bit, writes up to three payload bytes plus ID into the main mailbox, writes extension bytes for longer commands, and advances the mailbox index. Power-mode commands derive awake interval, RLBM, power state, BT coexistence values, and adaptive TSF beacon timing before sending H2C. Reserved-page download builds beacon, PS-Poll, null data, QoS null, and BT QoS null frames into a command xmit frame, inserts fake TX descriptors, sends the combined buffer, polls beacon-valid state, informs firmware of page locations, and restores beacon-related hardware bits.

## State and Persistence Behavior

State persists in `hal_com_data->LastHMEBoxNum`, `RegFwHwTxQCtrl`, MLME extension beacon timing counters, power-control `fw_psmode_iface_id`, firmware mailbox registers, reserved-page TX buffer contents, and firmware command state. The command buffers are stack-local or xmit-frame local.

## Dependencies and Integration Points

The file depends on H2C packing macros from `hal_com_h2c.h`, hardware registers (`REG_HMEBOX_*`, `REG_BCN_*`, `REG_FWHW_TXQ_CTRL`, `REG_CR`), xmit frame allocation/free/send helpers, MLME and security state, BT coexistence callbacks, fake TX descriptor generation, ODM rate bitmap selection, and HAL beacon-valid register helpers.

## Risks and Edge Cases

`_is_fw_read_cmd_down` busy-spins without delay. H2C payloads longer than seven bytes fail. Reserved-page construction must fit within reserved page size; overflow frees the frame but does not report error. Beacon construction in AP mode copies `pktlen` bytes after adding IE length, which is easy to misread and should be regression-tested. Poll loops can iterate up to 100 downloads and rely on `yield`. Many hardware bits are temporarily changed and must be restored even on failure paths.

## Test Signals

Tests should cover H2C mailbox selection, extension payloads, command length rejection, surprise removal, media status packing, MACID config packing, RSSI command packing, power-mode packing with and without BT control, reserved-page layout/page locations/overflow, beacon-valid retry loops, AP-mode BT coexist reserved-page download, and rate bitmap filtering before MACID config.

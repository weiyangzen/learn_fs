<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_intf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_intf.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_intf.h` defines the driver-wide HAL facade: hardware variable identifiers, default-definition query identifiers, ODM variable selectors, RF-change causes, wake reasons, and wrappers that upper driver code calls without knowing the RTL8723BS SDIO implementation details. The source was reviewed as a complete 269-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtw_hal_init`, `rtw_hal_deinit`, `rtw_hal_stop`, `rtw_hal_set_hwreg`, `rtw_hal_get_hwreg`, `rtw_hal_xmit`, `rtw_hal_mgnt_xmit`, `rtw_hal_init_recv_priv`, `rtw_hal_update_ra_mask`, `rtw_hal_read_bbreg`, `rtw_hal_write_rfreg`, `rtw_hal_fill_h2c_cmd`, `SetHwReg8723BS`, `GetHwReg8723BS`, and the `HW_VAR_*`, `HAL_DEF_*`, and `HAL_ODM_*` enums.

## Control Flow

Callers route initialization, register access, channel changes, power-save H2C commands, C2H handling, and transmit/receive setup through the generic `rtw_hal_*` entry points; the RTL8723BS-specific implementation interprets the `HW_VAR_*` selector and updates MAC, BB, RF, firmware, or descriptor state.

## State and Persistence Behavior

The header owns no storage but standardizes mutable adapter state: efuse data, RF state, CAM entries, beacon timing, rate adaptation, MACID sleep, firmware power state, and queue configuration. Values persist in `struct adapter` fields, hardware registers, and firmware mailboxes.

## Dependencies and Integration Points

Depends on common Realtek types such as `struct adapter`, `struct xmit_frame`, `struct sta_info`, `enum channel_width`, bit macros, and the chip-specific 8723B HAL implementation. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

The selector enums are ABI-like contracts between generic code and chip HAL callbacks; reordering or mismatching payload sizes can silently program the wrong hardware variable. Power-save and CAM selectors are especially high risk because failures show as hangs, dropped traffic, or broken encryption.

## Test Signals

Build coverage for all rtl8723bs objects, suspend/resume and IPS/LPS smoke tests, association/disassociation with WPA/WPA2, C2H/H2C event logging, channel switching, and TX/RX traffic under rate-adaptation changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_intf.h -->

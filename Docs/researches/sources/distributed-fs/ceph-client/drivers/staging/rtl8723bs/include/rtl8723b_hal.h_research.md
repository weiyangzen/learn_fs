<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_hal.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_hal.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_hal.h` is the central RTL8723B HAL header, defining firmware metadata, reserved-page constants, EFUSE sizes, HAL private data fields, chip init/deinit hooks, register access, interrupt control, C2H handlers, and BT firmware download declarations. The source was reviewed as a complete 243-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct rt_firmware`, `struct hal_com_data`, `struct hal_spec_t`, `rtl8723b_FirmwareDownload`, `rtl8723b_InitAntenna_Selection`, `rtl8723b_init_default_value`, `rtl8723b_InitBeaconParameters`, `rtl8723b_SetHalODMVar`, `SetHwReg8723B`, `GetHwReg8723B`, `rtl8723b_set_hal_ops`, `rtl8723bs_set_hal_ops`, `c2h_handler_8723b`, and EFUSE/reserved-page constants.

## Control Flow

Probe-time code allocates and fills HAL data, downloads firmware, initializes MAC/BB/RF/DM, sets SDIO-specific ops, and later services register operations, interrupts, and firmware C2H notifications.

## State and Persistence Behavior

Defines the main HAL state carrier: firmware version/signature, RF type/path, channel/bandwidth, antenna selection, efuse maps, transmit power tables, reserved-page offsets, interrupt masks, and BT coexistence fields.

## Dependencies and Integration Points

Includes or coordinates with `hal_intf.h`, `hal_phy_cfg.h`, `rtl8723b_cmd.h`, `rtl8723b_dm.h`, `rtl8723b_spec.h`, `rtw_efuse.h`, and SDIO HAL/ops. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

This is a high-blast-radius contract. Field layout changes affect many implementation files, and firmware/efuse size constants must match silicon and firmware images.

## Test Signals

Full driver probe, firmware download/version reporting, efuse parsing, interrupt enable/disable, C2H event handling, channel/rate/power tests, and unload/reload loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_hal.h -->

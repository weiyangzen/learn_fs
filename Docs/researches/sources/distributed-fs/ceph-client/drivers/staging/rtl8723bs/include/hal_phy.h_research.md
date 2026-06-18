<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy.h` provides common PHY constants, RF path and RF type enums, register bit masks, and helper prototypes used by baseband/RF configuration code. The source was reviewed as a complete 73-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `enum rf_path`, `enum rf_type`, `MAX_RF_PATH`, `MAX_TX_COUNT`, `MAX_REGULATION_NUM`, `MAX_RFDEPENDCMD_CNT`, `MAX_POSTCMD_CNT`, and PHY helper declarations used by chip-specific PHY config files.

## Control Flow

No runtime flow is implemented here; it supplies vocabulary consumed by register programming routines that query and set BB/RF registers during initialization, channel changes, calibration, and power-index updates.

## State and Persistence Behavior

All state is external: RF path selection, per-rate power data, and channel/bandwidth configuration live in HAL data and hardware registers.

## Dependencies and Integration Points

Used by `hal_phy_cfg.h`, `rtl8723b_rf.h`, `rtw_rf.h`, and chip calibration/configuration implementation files. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

RF enum or limit mismatches can make loops skip paths or write beyond path-specific arrays. Constants must match the single-stream 2.4 GHz 8723B device.

## Test Signals

Compile-time include coverage, PHY init on real or emulated SDIO device, channel/bandwidth changes, and register trace comparison against known-good initialization tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy.h -->

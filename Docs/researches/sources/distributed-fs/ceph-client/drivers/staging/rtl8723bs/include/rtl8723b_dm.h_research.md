<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_dm.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_dm.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_dm.h` declares RTL8723B dynamic management hooks for initializing ODM, watchdog processing, low-power watchdog work, antenna selection, and dynamic transmit-power tracking. The source was reviewed as a complete 33-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `rtl8723b_init_dm_priv`, `rtl8723b_deinit_dm_priv`, `rtl8723b_InitHalDm`, `rtl8723b_HalDmWatchDog`, `rtl8723b_HalDmWatchDog_in_LPS`, `rtl8723b_hal_dm_in_lps`, `AntDivBeforeLink8723B`, and `odm_DIGbyRSSI_LPS`.

## Control Flow

After HAL initialization, ODM state is initialized; periodic watchdog and low-power watchdog paths adjust gain, antenna, and rate-related dynamic behavior based on link and signal state.

## State and Persistence Behavior

Updates HAL/ODM private state, antenna selection, DIG thresholds, and dynamic TX power settings kept in adapter/HAL structures.

## Dependencies and Integration Points

Integrates with PHY, HAL, MLME link state, power-control LPS paths, and station RSSI tracking. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Watchdog work can race with suspend, LPS, or disconnect. Bad RSSI/DIG decisions can reduce throughput or link stability.

## Test Signals

Link under changing RSSI, LPS watchdog exercise, antenna diversity before/after association, and watchdog during suspend/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_dm.h -->

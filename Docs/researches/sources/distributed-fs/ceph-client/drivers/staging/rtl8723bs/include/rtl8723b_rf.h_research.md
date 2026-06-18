<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_rf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_rf.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_rf.h` declares RTL8723B RF front-end configuration entry points. The source was reviewed as a complete 17-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `PHY_RF6052_Config8723B` and `PHY_RF6052SetBandwidth8723B`.

## Control Flow

PHY initialization configures the RF6052 path; channel/bandwidth changes call the bandwidth helper to keep RF and BB settings aligned.

## State and Persistence Behavior

Persistent effects are RF register values and HAL bandwidth state.

## Dependencies and Integration Points

Used by `hal_phy_cfg.h` implementation and RF register access helpers. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

RF register programming must match the device path count and channel width; mistakes produce weak or absent RF output.

## Test Signals

RF init success, channel/bandwidth switches, throughput at 20/40 MHz where supported, and register trace comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtl8723b_rf.h -->

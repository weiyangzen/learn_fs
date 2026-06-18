<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pwr_seq.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pwr_seq.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pwr_seq.h` encodes RTL8723B power transition tables as `WLAN_PWR_CFG` macro initializers for POFF, PDN, card-emulation, active, LPS, software LPS, suspend, and card-disabled states. The source was reviewed as a complete 226-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `RTL8723B_TRANS_CARDEMU_TO_ACT`, `RTL8723B_TRANS_ACT_TO_CARDEMU`, `RTL8723B_TRANS_CARDEMU_TO_SUS`, `RTL8723B_TRANS_SUS_TO_CARDEMU`, `RTL8723B_TRANS_CARDEMU_TO_PDN`, `RTL8723B_TRANS_ACT_TO_LPS`, `RTL8723B_TRANS_LPS_TO_ACT`, `RTL8723B_TRANS_ACT_TO_SWLPS`, `RTL8723B_TRANS_SWLPS_TO_ACT`, and `RTL8723B_TRANS_END` plus their step counts.

## Control Flow

The power-sequence executor iterates these tables, filters entries by chip cut/fab/interface, and performs register writes, polling, and delays to move the SDIO/USB/PCI-capable core between power states.

## State and Persistence Behavior

Persistent effects are MAC and SDIO local register values controlling LDOs, isolation, reset, suspend, GPIO wake, XTAL ownership, and RF shutdown.

## Dependencies and Integration Points

Depends on `HalPwrSeqCmd.h` for `WLAN_PWR_CFG`, command codes, masks, and delay constants; consumed by HAL power-on/off and IPS/LPS code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

These are hardware sequencing contracts. Entry order, masks, and polling conditions must not drift from silicon documentation; errors can wedge the device, break wake, or leave power rails enabled.

## Test Signals

Cold probe, remove/reprobe, suspend/resume, IPS enter/leave, LPS enter/leave, wake-on-wireless scenarios, and register trace comparison to vendor sequence tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_pwr_seq.h -->

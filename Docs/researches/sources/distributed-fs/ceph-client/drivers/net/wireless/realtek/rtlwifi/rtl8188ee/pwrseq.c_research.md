# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/pwrseq.c

## Purpose

`pwrseq.c` materializes the RTL8188EE power transition tables declared as macros in `pwrseq.h`. These arrays are consumed by the shared rtlwifi power-sequence parser to move the NIC between card emulation, active, suspend, power-down/card-disabled, radio-off, and low-power states.

## Important APIs And Data

The file defines `struct wlan_pwr_cfg` arrays: `rtl8188ee_power_on_flow`, `rtl8188ee_radio_off_flow`, `rtl8188ee_card_disable_flow`, `rtl8188ee_card_enable_flow`, `rtl8188ee_suspend_flow`, `rtl8188ee_resume_flow`, `rtl8188ee_hwpdn_flow`, `rtl8188ee_enter_lps_flow`, and `rtl8188ee_leave_lps_flow`. Each array concatenates one or more transition macros and ends with `RTL8188EE_TRANS_END`.

## Control Flow

There is no executable function in this file. Runtime control flow occurs when callers such as `_rtl88ee_init_mac()` and `_rtl88ee_poweroff_adapter()` pass these arrays to `rtl_hal_pwrseqcmdparsing()`. The parser walks array entries, applies interface/fab/cut masks, performs writes, polls, delays, and stops at the end command.

## State And Persistence Behavior

The arrays are static driver data with no mutable state. Their entries cause persistent hardware state changes when parsed: MAC reset bits, suspend bits, RF-off writes, TX pause, DMA/WMAC reset, RPWM writes, BB clock and TSF clock changes, and card power-down controls.

## Dependencies And Integration Points

`pwrseq.c` depends on `../pwrseqcmd.h` for `struct wlan_pwr_cfg` and command definitions, and on `pwrseq.h` for transition macros and array size expressions. `hw.c` integrates these arrays into MAC init and adapter poweroff. The arrays are also exposed through aliases in `pwrseq.h`.

## Risks And Test Signals

Array size macros must match the number of entries emitted by transition macros plus the end marker; a mismatch can truncate or leave uninitialized entries. The `rtl8188ee_card_enable_flow` size expression uses ACT-to-CARDEMU and CARDEMU-to-PDN step counts even though the initializer uses CARDDIS-to-CARDEMU and CARDEMU-to-ACT; the counts are currently both 10, but this is fragile. Tests should verify parser success for NIC enable, disable, suspend/resume, radio off, and LPS enter/leave, including PCIe interface mask filtering and polling timeout behavior.

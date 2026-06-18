# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/pwrseq.c

## Purpose

`pwrseq.c` materializes RTL8812 and RTL8821A power transition flows as `struct wlan_pwr_cfg` arrays. The common power-sequence executor parses these arrays and performs the register writes, polling operations, delays, and end markers defined by `pwrseq.h`.

## Important APIs and Data

RTL8812 arrays: `rtl8812_power_on_flow`, `rtl8812_radio_off_flow`, `rtl8812_card_disable_flow`, `rtl8812_card_enable_flow`, `rtl8812_suspend_flow`, `rtl8812_resume_flow`, `rtl8812_hwpdn_flow`, `rtl8812_enter_lps_flow`, and `rtl8812_leave_lps_flow`.

RTL8821A arrays: `rtl8821A_power_on_flow`, `rtl8821A_radio_off_flow`, `rtl8821A_card_disable_flow`, `rtl8821A_card_enable_flow`, `rtl8821A_suspend_flow`, `rtl8821A_resume_flow`, `rtl8821A_hwpdn_flow`, `rtl8821A_enter_lps_flow`, and `rtl8821A_leave_lps_flow`.

Each array is sized from `*_STEPS` constants plus `*_TRANS_END_STEPS`, and initialized by concatenating transition macros such as `RTL8812_TRANS_CARDEMU_TO_ACT` and `RTL8812_TRANS_END`.

## Control Flow

This file contains data, not algorithms. Power code elsewhere selects one of these arrays through aliases in `pwrseq.h`, then iterates until a `PWR_CMD_END` entry. Power-on moves card emulation to active; radio-off moves active to card emulation; card disable/enable and suspend/resume combine intermediate transitions; hardware power-down enters PDN; LPS entry pauses TX and gates MAC/BB/RF state; LPS leave wakes firmware/host power mechanisms and reenables WMAC/BB.

## State and Persistence Behavior

The arrays are compiled into the driver and should be treated as immutable transition tables. Runtime state changes occur only when the common executor applies them to hardware, affecting MAC, SDIO/USB/PCIe local registers, GPIO wake controls, analog isolation, LDO sleep, WL suspend, firmware reset, DMA, TX pause, BB/RF clocks, and WMAC TRX state.

## Dependencies and Integration Points

The file includes `../pwrseqcmd.h` for `struct wlan_pwr_cfg`, command IDs, masks, base addresses, and delay constants, and local `pwrseq.h` for transition macros and declarations. It is consumed by RTL8821AE hardware and power-management code through aliases such as `RTL8812_NIC_PWR_ON_FLOW` and `RTL8821A_NIC_PWR_ON_FLOW`.

## Risks and Edge Cases

- Transition macros include PCIe, USB, and SDIO masked entries; interface masks must be correct.
- Some array size expressions use logically mismatched but currently numerically compatible step constants, which is a maintenance hazard.
- Since this file is pure data, functional regressions from macro changes require hardware power-cycle, suspend/resume, and LPS testing.

## Test Signals

Compile after any `*_STEPS` or transition macro change. Probe hardware and exercise NIC power-on, radio off/on, card disable/enable, suspend/resume, hardware power-down, IPS, and LPS entry/leave while checking that the power-sequence executor reaches `PWR_CMD_END`.

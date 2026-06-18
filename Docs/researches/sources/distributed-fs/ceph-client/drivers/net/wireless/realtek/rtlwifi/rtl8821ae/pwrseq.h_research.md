# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/pwrseq.h

## Purpose

`pwrseq.h` defines RTL8812 and RTL8821A hardware power-state transition scripts for the common `rtlwifi` power-sequence executor. It describes sequences for moving among card emulation, active, suspend, card-disable, power-down, and low-power states, then declares concrete arrays in `pwrseq.c` and provides chip-specific alias names for callers.

## Important APIs, Data, and Macros

Step-count constants size the arrays in `pwrseq.c`. RTL8812 transition macros include card-emulation-to-active, active-to-card-emulation, suspend/resume, card-disable/card-enable, power-down, LPS entry/leave, and end markers. RTL8821A transition macros mirror the same state graph with additional LDO, analog isolation, GPIO9 wake, BT/GPS pin, DPDT/PAPE/LNA, and XTAL trim steps.

Extern declarations expose all `rtl8812_*_flow` and `rtl8821A_*_flow` arrays. Alias macros such as `RTL8812_NIC_PWR_ON_FLOW`, `RTL8812_NIC_DISABLE_FLOW`, `RTL8821A_NIC_RESUME_FLOW`, and `RTL8821A_NIC_LPS_LEAVE_FLOW` provide the names used by hardware code.

## Control Flow

The common executor walks arrays built from these macros. For each entry it checks cut/fab/interface masks, applies a write/poll/delay command to the selected base address, and stops at `PWR_CMD_END`. Polling entries wait for conditions such as power ready, MAC-off completion, TX-empty, TSF clock, SDIO suspend state, or LPS wake state.

## State and Persistence Behavior

The macros define hardware side effects that become real when executed: enabling rails, releasing reset, disabling suspend/power-down, switching control pins, enabling interrupts, turning off RF, isolating analog/digital domains, entering LDO sleep, configuring GPIO wake, pausing TX, gating BB/RF/MAC blocks, and waking firmware/host power mechanisms. The scripts are compiled into the driver and are not persisted outside the module.

## Dependencies and Integration Points

`pwrseq.h` includes `../pwrseqcmd.h` for `struct wlan_pwr_cfg`, commands, masks, base addresses, and delays. It also includes `../btcoexist/halbt_precomp.h`, reflecting BT/GPS/coexistence interactions in some power transitions. The macros are expanded by `pwrseq.c` and consumed indirectly by hardware power-management code.

## Risks and Edge Cases

- The macros are dense register scripts; one-bit changes can break boot, suspend/resume, wake, LPS, or coexistence.
- USB/SDIO entries are present in a PCIe driver subtree and rely on interface masks.
- Step-count constants must stay large enough for the emitted macro entries.
- Polling commands can time out if mask/value pairs do not match a chip cut or interface.
- GPIO9 wake, WL suspend, analog isolation, and LDO sleep entries are platform-sensitive.

## Test Signals

Build-test after macro or step-count edits. On RTL8812AE and RTL8821AE hardware, run cold probe, warm reboot, module reload, RF off/on, suspend/resume, hardware power-down, and LPS entry/leave. Executor logging should show expected interface/cut masking and a final `PWR_CMD_END`.

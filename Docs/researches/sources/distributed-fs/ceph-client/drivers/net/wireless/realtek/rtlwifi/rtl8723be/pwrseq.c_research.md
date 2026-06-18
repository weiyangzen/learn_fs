# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/pwrseq.c

## Purpose
Defines RTL8723B power-transition flow arrays consumed by the common Realtek power-sequence parser. These arrays encode card-emulation, active, suspend, power-down, card-disable, and low-power-state transitions for PCI operation.

## Important APIs, Types, And Functions
The file exports `struct wlan_pwr_cfg` arrays: `rtl8723B_power_on_flow`, `rtl8723B_radio_off_flow`, `rtl8723B_card_disable_flow`, `rtl8723B_card_enable_flow`, `rtl8723B_suspend_flow`, `rtl8723B_resume_flow`, `rtl8723B_hwpdn_flow`, `rtl8723B_enter_lps_flow`, and `rtl8723B_leave_lps_flow`. Each is composed from macros in `pwrseq.h` and terminated with `RTL8723B_TRANS_END`.

## Control Flow
There is no local executable control flow. `rtl_hal_pwrseqcmdparsing()` walks these arrays when `hw.c` initializes MAC power, powers off the adapter, disables/enables the card, or enters/leaves firmware LPS.

## State And Persistence
The arrays are static configuration data. The persistent effects occur when the parser writes hardware power, clock, reset, isolation, and low-power registers according to the macro-expanded commands.

## Dependencies And Integration Points
Depends on `../pwrseqcmd.h` and `pwrseq.h` for command structure and transition macro definitions. Integrated by `hw.c` through constants such as `RTL8723_NIC_ENABLE_FLOW`, `RTL8723_NIC_DISABLE_FLOW`, and `RTL8723_NIC_LPS_ENTER_FLOW`.

## Risks
Array sizing must match the step-count macros plus end marker. Wrong transition ordering can leave the chip in card-emulation, suspend, PDN, or active states incorrectly, which affects firmware download, RF power, and wake behavior. Since this is data-driven, errors surface only at runtime through parser failures or dead hardware.

## Test Signals
Probe power-on, card disable, IPS/LPS entry/exit, suspend/resume-like flows, and hardware power-down should complete without power-sequence parser failures. Hardware signals include successful register access after enable, firmware download after active transition, and low idle power after LPS/card-disable transitions.

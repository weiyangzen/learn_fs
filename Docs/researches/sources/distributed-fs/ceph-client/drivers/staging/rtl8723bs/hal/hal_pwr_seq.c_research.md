# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_pwr_seq.c

## Purpose

`hal_pwr_seq.c` defines RTL8723B power-transition scripts as `struct wlan_pwr_cfg` arrays. These arrays are parsed elsewhere to move the chip among card-emulation, active, radio-off, card-disable, suspend, resume, hardware power-down, firmware LPS, and software LPS states. The source was read as a complete 130-line file.

## Important APIs, Types, and Functions

The exported data objects are `rtl8723B_power_on_flow`, `rtl8723B_radio_off_flow`, `rtl8723B_card_disable_flow`, `rtl8723B_card_enable_flow`, `rtl8723B_suspend_flow`, `rtl8723B_resume_flow`, `rtl8723B_hwpdn_flow`, `rtl8723B_enter_lps_flow`, `rtl8723B_leave_lps_flow`, `rtl8723B_enter_swlps_flow`, and `rtl8723B_leave_swlps_flow`. The arrays are built from macros in `hal_pwr_seq.h`, such as `RTL8723B_TRANS_CARDEMU_TO_ACT` and `RTL8723B_TRANS_END`.

## Control Flow

There is no executable control flow in this file. Runtime power-control code selects the appropriate array and interprets each `wlan_pwr_cfg` entry in sequence until `RTL8723B_TRANS_END`, performing register writes, polling, delays, or command actions defined by the macro-expanded entries.

## State and Persistence Behavior

The file stores static transition tables only. Hardware power state changes persist in device registers and power domains after the parser executes the selected flow.

## Dependencies and Integration Points

It depends entirely on `hal_pwr_seq.h` for array lengths and transition macro contents. It integrates with RTL8723BS power-on, suspend/resume, IPS/LPS, card-disable, and radio-off code that consumes these arrays.

## Risks and Edge Cases

Array length expressions must match the number of macro-expanded entries; a macro/table drift can create truncation or extra uninitialized entries. The card-disable and card-enable arrays use lengths containing `RTL8723B_TRANS_CARDEMU_TO_PDN_STEPS` while one initializer uses `CARDEMU_TO_CARDDIS`, so the header definitions must stay consistent. Incorrect transition order can leave firmware or SDIO state inaccessible.

## Test Signals

Compile-time array sizing, parser dry-runs that count transitions to `END`, power-cycle smoke tests, suspend/resume tests, LPS enter/leave tests, and register-trace comparisons with Realtek reference sequences are the main signals.

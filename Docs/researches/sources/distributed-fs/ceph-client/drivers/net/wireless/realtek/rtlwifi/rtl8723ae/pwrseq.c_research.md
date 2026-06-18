# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/pwrseq.c

Purpose: `pwrseq.c` materializes RTL8723A power-transition macros from `pwrseq.h` into `struct wlan_pwr_cfg` arrays consumed by the common rtlwifi power-sequence parser.

Important APIs/data: exported arrays are `rtl8723A_power_on_flow`, `rtl8723A_radio_off_flow`, `rtl8723A_card_disable_flow`, `rtl8723A_card_enable_flow`, `rtl8723A_suspend_flow`, `rtl8723A_resume_flow`, `rtl8723A_hwpdn_flow`, `rtl8723A_enter_lps_flow`, and `rtl8723A_leave_lps_flow`.

Control flow: no functions execute here. Runtime control flow occurs when callers pass these arrays to `rtl_hal_pwrseqcmdparsing`, mainly in MAC init, poweroff, LPS entry/leave, and card enable/disable paths. Each array concatenates transition macros and terminates with `RTL8723A_TRANS_END`.

State and persistence: the arrays are static driver data. They encode register offsets, interface masks, command types, bit masks, values, polling waits, and delays. Hardware persistence is produced by the parser writing the encoded registers.

Dependencies/integration: depends on `pwrseqcmd.h` for `struct wlan_pwr_cfg`, masks, base addresses, and command constants, and on `pwrseq.h` macro definitions. Used by `hw.c` through the `RTL8723_NIC_*_FLOW` aliases.

Risks: array length declarations must match the number of macro entries. Several arrays use historical step-count names that are larger than actual macro entries, which is safe for initializer capacity but can hide stale documentation. A wrong command or missing `TRANS_END` would break probe, shutdown, suspend, or LPS.

Test signals: successful power-on during probe, RF-off/card-disable without hangs, LPS entry/leave, suspend/resume parser behavior if wired, and absence of power-sequence polling timeouts.

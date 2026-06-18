# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/fw.h

## Purpose

`fw.h` defines the RTL8188EE firmware interface: firmware image size and polling constants, firmware header detection, firmware power-state bit encodings, H2C command IDs, H2C payload lengths, payload packing helpers, and the public firmware helper prototypes implemented in `fw.c`.

## Important APIs, Types, And Constants

`enum rtl8188e_h2c_cmd` assigns command IDs for reserved pages, join-BSS report, keepalive, AP offload, power mode, P2P power-save offload, WOWLAN, AOAC, and the driver RA-mask extension. The `FW_PS_*` macros encode RPWM/CPWM and firmware low-power states used by `hw.c` clock and firmware-LPS logic. Inline setters such as `set_h2ccmd_pwrmode_parm_mode()`, `set_h2ccmd_pwrmode_parm_rlbm()`, and related macros pack command payloads in firmware-defined byte layouts.

The public prototypes are `rtl88e_download_fw()`, `rtl88e_fill_h2c_cmd()`, `rtl88e_firmware_selfreset()`, `rtl88e_set_fw_pwrmode_cmd()`, `rtl88e_set_fw_joinbss_report_cmd()`, `rtl88e_set_fw_ap_off_load_cmd()`, `rtl88e_set_fw_rsvdpagepkt()`, and `rtl88e_set_p2p_ps_offload_cmd()`.

## Control Flow And Integration

The header has no runtime control flow. It is included by `fw.c` for command construction and by `hw.c` for firmware power-state constants, H2C routing, and firmware reset/download integration. `pagenum_128()` supports reserved-page sizing semantics, while the command length constants constrain `rtl88e_fill_h2c_cmd()` callers.

## State And Persistence Behavior

No state is stored in this header, but macro values define persistent hardware/firmware protocol semantics. Changing IDs, lengths, or bit definitions changes on-wire mailbox payloads and can break firmware compatibility.

## Dependencies, Risks, And Test Signals

The macros depend on little-endian bitfield helpers such as `SET_BITS_TO_LE_1BYTE()` and `u8p_replace_bits()`. There is a duplicated `FW_PWR_STATE_ACTIVE`/`FW_PWR_STATE_RF_OFF` definition pair, which currently resolves identically but should be kept in mind during maintenance. The enum entry `H2C_88E_P2P_PS_OFFLOAD = 024` is an octal literal in C syntax; it equals decimal 20, not decimal 24. Build tests, static checks for payload length versus mailbox capacity, and hardware command smoke tests are the main signals for this file.

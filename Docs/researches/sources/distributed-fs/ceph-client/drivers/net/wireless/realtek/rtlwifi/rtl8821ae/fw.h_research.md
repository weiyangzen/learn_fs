# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/fw.h

## Purpose
This header defines the firmware-facing ABI used by the RTL8821AE/RTL8812AE driver. It contains firmware image limits, download polling constants, firmware-header signature tests, H2C command IDs and payload lengths, firmware power-save bit definitions, command-packing macros, reserved-page location macros, and exported firmware helper prototypes.

The header is the compact contract between C driver code and the closed firmware running on the device MCU. Small layout mistakes here change the bytes written into firmware mailboxes.

## Important APIs, Types, And Functions
Firmware download constants include `FW_8821AE_SIZE`, start/end addresses, 4 KiB page size, polling delay, and polling timeout count. Header-detection macros `IS_FW_HEADER_EXIST_8812()` and `IS_FW_HEADER_EXIST_8821()` identify Realtek firmware signatures after endian conversion.

`enum rtl8821a_h2c_cmd` defines firmware command IDs for reserved pages, media status report, keep-alive, disconnect decision, AP offload, reserved beacon/probe response, power-save mode, P2P PS, WoWLAN, remote wake, AOAC global info, AOAC reserved page, RSSI report, RA mask, and related commands. Payload-length macros define the expected byte counts for each command family.

Power-save macros define RPWM/CPWM state bits, low-power checks, active/RF-off states, and helpers to inspect ACK/clock/RF/interrupt bits. Command-packing macros write individual fields into byte arrays using `u8p_replace_bits()` or direct byte stores. Public prototypes export firmware download, H2C send, self-reset, LPS/media/AP/WoWLAN/remote wake/keep-alive/disconnect/global-info commands, reserved-page download for both 8821 and 8812, P2P PS offload, and C2H RA report handling.

## Control Flow
The header has no runtime flow, but its definitions drive `fw.c`. Firmware download uses size/page/poll constants and signature macros. H2C command builders allocate fixed-size byte arrays using the length macros, fill them with `SET_*` macros, and send them with IDs from `enum rtl8821a_h2c_cmd`. Power-save flows use `FW_PS_*` macros to encode driver and firmware state. Reserved-page flows use `SET_H2CCMD_RSVDPAGE_LOC_*` and AOAC location macros to tell firmware where packet templates were placed.

The conditional `USE_SPECIFIC_FW_TO_SUPPORT_WOWLAN` and `USE_OLD_WOWLAN_DEBUG_FW` definitions affect whether a WoWLAN firmware-redownload helper is declared and how long remote wake control payloads are.

## State And Persistence
No state is allocated in the header. It defines constants and byte layouts for state stored in firmware, hardware registers, `rtlhal`, `rtlps`, and command buffers on the stack. The macros mutate caller-provided arrays in place; their effects persist only after `rtl8821ae_fill_h2c_cmd()` writes them to firmware mailboxes.

Because this is an ABI header, its values are effectively persistent across all compiled driver instances. Any change must match the firmware version loaded by `fw.c`.

## Dependencies And Integration Points
The header includes `def.h` and depends on kernel bit macros, endian helpers, `u8p_replace_bits()`, and Realtek firmware structures. It is included by `fw.c` and `dm.c` and referenced by power management, WoWLAN, P2P, and C2H dispatch code. The exported functions are called from chip init, suspend/resume, LPS, AP/P2P setup, reserved-page setup, and firmware event handling paths.

It also integrates with Bluetooth coexistence indirectly because `rtl8821ae_set_fw_pwrmode_cmd()` packs coexistence-selected values into fields defined here.

## Risks
The main risk is byte-layout mismatch with firmware. Many `SET_*` macros do unguarded pointer arithmetic and direct stores; they assume the caller allocated at least the matching `H2C_..._LEN` bytes. Some command comments and IDs are inherited from older chips, and `H2C_8821AE_P2P_PS_OFFLOAD = 024` is an octal literal in C, so maintainers must treat command IDs carefully. `FW_PWR_STATE_ACTIVE` and `FW_PWR_STATE_RF_OFF` are defined twice, which is harmless only while values remain identical.

Power-save bit names are easy to confuse because 8821AE RPWM values define all-on/RF-on/RF-off states differently from the older 92C macros in the same header. Future firmware command expansion beyond seven H2C bytes would require coordinated changes in both this header and `fw.c` mailbox writing.

## Test Signals
Compile tests should catch prototype drift and missing macro dependencies. Runtime validation should inspect H2C byte arrays for each command ID, especially power mode, WoWLAN, remote wake, keep-alive, AOAC global info, AOAC reserved-page locations, and disconnect decision. Firmware compatibility tests should verify command IDs and lengths against the loaded firmware, including both normal and WoWLAN firmware. Static analysis should check all macro callers allocate buffers of the declared length and do not pass overlapping or too-short arrays.

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/fw.c

## Purpose

`fw.c` handles RTL8188EE firmware download, firmware self-reset, host-to-controller mailbox commands, reserved-page packet upload, firmware power-mode commands, AP offload, join-BSS reporting, and P2P power-save offload programming. It is the bridge between the host driver and the 8051-style firmware running on the NIC.

## Important APIs And Functions

`rtl88e_download_fw()` consumes `rtlhal->pfirmware` and `rtlhal->fwsize`, skips a Realtek firmware header when present, enables firmware download mode, writes firmware pages, disables download mode, and waits for checksum and firmware-ready bits. `rtl88e_fill_h2c_cmd()` validates `rtlhal->fw_ready`, copies up to 7 bytes into a temporary H2C buffer, and delegates to `_rtl88e_fill_h2c_command()`. The private H2C writer serializes mailbox access with `h2c_lock` and `rtlhal->h2c_setinprogress`, cycles four HME boxes, waits for firmware to clear the target box through `REG_HMETFR`, and writes normal or extended mailbox registers.

Public command helpers include `rtl88e_set_fw_pwrmode_cmd()`, `rtl88e_set_fw_joinbss_report_cmd()`, `rtl88e_set_fw_ap_off_load_cmd()`, `rtl88e_set_fw_rsvdpagepkt()`, and `rtl88e_set_p2p_ps_offload_cmd()`. `rtl88e_firmware_selfreset()` toggles the MCU reset bit in `REG_SYS_FUNC_EN + 1`.

## Control Flow

Firmware download starts only if the firmware pointer exists. Existing firmware-ready state in `REG_MCUFWDL` causes a self-reset before a fresh load. `_rtl88e_write_fw()` pads firmware using `rtl_fill_dummy()`, splits it into 4 KiB pages, and writes each page through `rtl_fw_page_write()`. `_rtl88e_fw_free_to_go()` polls for `FWDL_CHKSUM_RPT`, sets `MCUFWDL_RDY`, clears `WINTINI_RDY`, resets the firmware, and then polls until `WINTINI_RDY` appears.

H2C command flow is serialized because firmware mailboxes are shared state. If another H2C command is active, the caller waits in 100 us intervals up to a hard limit. For each command, the current `last_hmeboxnum` selects the mailbox register pair, the driver waits for firmware to read the box, writes element ID plus payload bytes, advances the mailbox number modulo four, and clears the in-progress flag.

Reserved-page flow builds static 128-byte-page templates for beacon, PS-Poll, null data, and probe response, patches MAC/BSSID/AID fields from `rtl_mac`, sends the entire reserved buffer via `rtl_cmd_send_packet()`, and then informs firmware of page locations by H2C command. P2P power-save flow programs CTWindow, up to two NoA descriptors, TSF-adjusted start times, P2P role flags, and then sends the compact offload state to firmware.

## State And Persistence Behavior

Firmware state persists in NIC memory and in `rtlhal`: `fw_version`, `fw_subversion`, `fw_ready`, `last_hmeboxnum`, `h2c_setinprogress`, and `p2p_ps_offload`. `reserved_page_packet` is a file-static mutable buffer; each reserved-page upload rewrites address fields in place. P2P offload updates hardware NoA registers and the firmware offload byte structure. Power-mode commands reflect current `rtl_ps_ctl` fields such as smart PS and awake interval.

## Dependencies And Integration Points

The file depends on shared firmware header definitions, efuse/base/core helpers, raw MMIO helpers, H2C field macros from `fw.h`, 802.11 frame field setters, SKB allocation, and `rtl_cmd_send_packet()`. `hw.c` calls firmware download during initialization and routes `HW_VAR_H2C_*` operations into these helpers. Power management in `hw.c` depends on the firmware power-mode command emitted here.

## Risks And Edge Cases

`rtl88e_download_fw()` returns `0` even when `_rtl88e_fw_free_to_go()` reports an error after printing an error, so callers relying only on the return value may mark firmware ready incorrectly. H2C wait loops are bounded but busy-wait with microsecond delays, which can stall callers. The H2C API copies `cmd_len` bytes into an 8-byte temporary buffer and supports only 1-7 byte payloads in the private writer; callers must preserve that contract. `reserved_page_packet` is global mutable state and can race if multiple uploads occur concurrently. P2P NoA count handling mutates `noa_count_type[]` while adjusting start times.

## Test Signals

Tests should check successful and failed firmware download paths, firmware header stripping, page writes with exact and partial 4 KiB sizes, checksum/ready polling timeouts, H2C serialization under concurrent callers, mailbox wraparound, no-command behavior when `fw_ready` is false, reserved-page packet address patching, AP offload fields, power-mode command bytes, and P2P NoA/CTWindow register programming across GO and client roles.

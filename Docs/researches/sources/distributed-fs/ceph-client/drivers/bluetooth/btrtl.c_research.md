# sources/distributed-fs/ceph-client/drivers/bluetooth/btrtl.c

## Purpose

`btrtl.c` is the Realtek Bluetooth support library used by transport drivers, especially `btusb` and HCI UART integrations. It identifies Realtek controller generations, loads matching firmware and optional config blobs, parses Realtek EPATCH formats, downloads firmware over vendor HCI commands, exposes UART config extraction, and installs Realtek-specific HCI quirks and devcoredump metadata.

## Important APIs, Types, and Functions

- `struct id_table` is the chip database. Match fields combine LMP subversion, HCI revision/version, bus type, and optional chip type with firmware/config names and capability flags such as `has_rom_version` and `has_msft_ext`.
- `struct btrtl_device_info` is the runtime firmware context. It owns selected `ic_info`, ROM version, firmware/config buffers, project ID, security key ID, and the ordered patch subsection list for EPATCH v2.
- `btrtl_initialize()` is the main discovery and firmware load entry point. It reads Realtek vendor registers, HCI local version, optional chip type and ROM version, matches `ic_id_table`, handles a "drop firmware" retry path, loads firmware/config files, and sets Microsoft vendor opcode support.
- `btrtl_download_firmware()` chooses the legacy RTL8723A download path or EPATCH path, then registers devcoredump support.
- `rtlbt_parse_firmware()` parses EPATCH v1 and dispatches v2 to `rtlbt_parse_firmware_v2()`. It validates signatures, parses the extension trailer for project ID, verifies project-to-LMP compatibility, selects the ROM-specific patch, and appends firmware version bytes.
- `rtlbt_parse_firmware_v2()`, `btrtl_parse_section()`, and `btrtl_insert_ordered_subsec()` parse prioritized patch/security/dummy subsections filtered by ECO and key ID.
- `rtl_download_firmware()` fragments payloads into `RTL_FRAG_LEN` 252-byte vendor command chunks using opcode `0xfc20`, marks the final fragment with bit `0x80`, and logs the post-download version.
- `btrtl_get_uart_settings()` parses Realtek config entries, especially offset `0x0c`, to return encoded device baudrate, converted controller baudrate, and flow-control state.
- `btrtl_set_quirks()`, `btrtl_setup_realtek()`, `btrtl_shutdown_realtek()`, and `btrtl_set_driver_name()` are exported helpers used by transport drivers.

## Control Flow

Initialization starts with vendor register `RTL_CHIP_SUBVER` and sometimes `RTL_CHIP_REV`; otherwise it reads `HCI_OP_READ_LOCAL_VERSION`. Some LMP IDs require an extra chip-type vendor command. The resulting identity is matched against `ic_id_table`. If no table entry is found on the first pass, the driver sends vendor command `0xfc66`, waits 200 ms, and retries version detection, allowing controllers in an odd initial firmware state to expose their normal identity.

For recognized chips, the helper reads ROM version if required, reads `RTL_SEC_PROJ` for `key_id`, loads firmware, and conditionally loads a config blob. Config files may be mandatory for UART chips, while USB chips often operate without one. `btrtl_download_firmware()` then chooses a setup routine by LMP family. RTL8723A expects a raw firmware file. Newer chips expect EPATCH data that is parsed, optionally concatenated with config, and sent in HCI vendor fragments.

## State and Persistence

State is transient and bound to `struct btrtl_device_info`; firmware/config buffers are copied from Linux firmware files and freed by `btrtl_free()`. The helper stores controller and firmware version strings in the transport-private `struct btrealtek_data` devcoredump area. Persistent behavior is entirely external: firmware files under `rtl_bt/` and optional config files determine runtime programming. No source-local persistent files or NVRAM writes are performed here.

## Dependencies and Integration Points

The file depends on the Bluetooth HCI core (`__hci_cmd_sync`, `hci_recv`, quirks, Microsoft opcode hooks, devcoredump), Linux firmware loading, unaligned access helpers, and `btrtl.h` wire-format declarations. Transport drivers call into it after their HCI device exists but before normal operation. `btusb.c` uses it for Realtek USB setup, shutdown, reset/coredump naming, WBS flags, Microsoft extension address filtering, and ALT6 mSBC behavior.

## Risks

Firmware parsing is security-sensitive because controller firmware blobs drive lengths, offsets, subsection counts, and pointer movement. The implementation has several size checks, but risks remain around malformed EPATCH v2 section accounting, integer/length mismatches, and trusting firmware-internal subsection pointers until copied. The `drop_fw` retry path sends a raw HCI command through `hdev->send` before normal setup, so transport readiness matters. Config handling skips config load when `key_id` is nonzero; regressions there can break UART baudrate extraction. Adding table entries is also risky because incorrect LMP/HCI/bus matching can load incompatible firmware.

## Test Signals

Useful signals include successful firmware request logs, `rom_version` and firmware version logs after download, absence of `EPATCH signature`, project mismatch, mandatory config, or fragment download errors, and working `HCI_OP_READ_LOCAL_VERSION` after download. Tests should cover known chip table matches, fallback firmware names such as `_v2.bin`, missing optional versus mandatory config, malformed EPATCH v1/v2 files, UART config offset parsing, and Realtek USB probe through `btusb_setup_realtek()`.

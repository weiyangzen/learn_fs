# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/cmd.h

Purpose: Defines wl1251 firmware command IDs, status codes, packed command payloads, scan/join/template/key structures, and command function prototypes.

Important APIs, types, and functions: Exports all functions implemented by `cmd.c`. Defines `WL1251_COMMAND_TIMEOUT`, `enum wl1251_commands`, `struct wl1251_cmd_header`, generic `struct wl1251_command`, status constants, memory read/write command payload, scan parameters/channels, join command, path enable/disable command, packet template command, VBM/TIM update, power-save params, trigger scan timeout, and key action/type/set-key payload.

Control flow: The structs are filled by command builders, sent through `wl1251_cmd_send()`, and interpreted by firmware. ACX commands reuse `struct wl1251_cmd_header` through `struct acx_header`.

State and persistence: Defines transient mailbox command payloads and firmware status values. No host state.

Dependencies and integration points: Includes `wl1251.h` and cfg80211; referenced by `acx.h`, `cmd.c`, TX/security setup, and boot/init code.

Risks: ABI mismatch in packed structs breaks firmware communication. `MAX_CMD_PARAMS` and fixed arrays bound mailbox payload sizes; callers must clamp template, scan, and key lengths. Status codes include driver-internal timeout/reset values mixed with firmware statuses.

Test signals: Compile with packed layout assumptions, command status decoding, scan channel limit handling, and key installation/removal across WEP/TKIP/AES.

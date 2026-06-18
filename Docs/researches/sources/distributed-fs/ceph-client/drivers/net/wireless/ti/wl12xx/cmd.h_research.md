# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/cmd.h

Purpose: Defines wl12xx command payload structures for INI/NVS firmware test commands and channel switching.

Important APIs and types: Test command IDs `TEST_CMD_INI_FILE_RADIO_PARAM`, `TEST_CMD_INI_FILE_GENERAL_PARAM`, and `TEST_CMD_INI_FILE_RF_EXTENDED_PARAM`; command structs for wl1271/wl128x general parameters, radio parameters, extended radio parameters, and `wl12xx_cmd_channel_switch`; prototypes for command helpers.

Control flow: No executable control flow. Struct definitions determine payload layout for `cmd.c`.

State and persistence: No stored state. Structures carry NVS-derived data into firmware and may carry updated general params back from firmware test commands.

Dependencies and integration points: Includes `conf.h` for RF compensation lengths. Depends on wlcore command header types and NVS parameter types via included headers.

Risks: Packed structure layouts are firmware ABI. Padding bytes are explicit and should not be removed. wl1271 and wl128x layouts differ and must not be interchanged.

Test signals: Firmware accepts test commands during hw init; FEM auto-detect and radio parameter programming work on both chip families.

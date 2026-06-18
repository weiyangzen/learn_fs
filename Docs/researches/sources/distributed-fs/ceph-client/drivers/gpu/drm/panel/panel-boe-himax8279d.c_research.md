# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-himax8279d.c

Purpose: Descriptor-driven MIPI DSI panel driver for BOE Himax8279d 8-inch and 10-inch 1200x1920 TFT LCD modules.

Important APIs/types/functions: `struct panel_cmd`, `struct panel_desc`, `struct panel_info`, `send_mipi_cmds`, panel prepare/enable/disable/unprepare/get_modes functions, shared `default_display_mode`, two large on-command arrays, two panel descriptors, OF match data, and DSI probe/remove.

Control flow: Probe selects the descriptor by compatible string, copies DSI mode flags/format/lanes, gets `pp18`, `pp33`, and `enable` GPIOs, attaches OF backlight, registers the panel, and attaches to the DSI host. Prepare powers GPIO rails in sequence, toggles enable reset, sends every descriptor command as a two-byte DCS write buffer, exits sleep mode, waits, sets display on, and waits again. Enable redundantly waits and sends display on. Disable sends display off; unprepare sends display off, sleep in, waits, and drops GPIOs.

State and persistence: State holds panel, DSI link, descriptor, and three GPIOs. Command tables encode all panel tuning and are static.

Dependencies and integration: Depends on DRM MIPI DSI, GPIO, OF match data, DRM panel, and optional backlight binding.

Risks: `send_mipi_cmds` ignores its `cmds` length argument and uses `desc->on_cmds_num`; descriptor counts must match arrays exactly. GPIOs use non-cansleep setters, so backing controllers must be atomic-safe. Regulators are included but not used. `get_modes` does not mark the mode preferred.

Test signals: Both compatibles, command count audit against array size, GPIO sequencing on hardware, DSI attach/remove, display-on redundancy tolerance, and panel mode/bpc reporting.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-abt-y030xx067a.c

Purpose: SPI/regmap DRM panel driver for Asia Better Technology Y030XX067A 320x480 DPI LCD panels.

Important APIs/types/functions: Defines register bit macros, `struct y030xx067a_info`, `struct y030xx067a`, `y030xx067a_init_sequence`, DRM panel funcs, SPI probe/remove, regmap config, display modes, and OF match data.

Control flow: Probe allocates a DPI `drm_panel`, initializes SPI regmap, reads match data, gets `power` regulator and reset GPIO, attaches optional OF backlight, and registers the panel. Prepare enables power, toggles reset, and writes the init register sequence. Enable sets `REG06_XPSAVE` and waits before backlight. Disable clears it; unprepare resets and disables power. `get_modes` duplicates 60 Hz and 50 Hz modes and sets bus format/flags.

State and persistence: Runtime state stores SPI, regmap, panel info, regulator, and reset GPIO. Register settings are reprogrammed on each prepare.

Dependencies and integration: Depends on SPI, REGMAP_SPI, GPIO, regulator, DRM panel, OF match data, media bus formats, and optional backlight phandle.

Risks: Any init sequence error aborts prepare and powers down. The panel has two modes but only marks preferred when there is exactly one, so neither mode is preferred here. Timing and register values are hardware-specific.

Test signals: SPI probe with compatible `abt,y030xx067a`, regmap write verification, reset polarity on hardware, mode enumeration for both refresh rates, backlight delay behavior, and remove path disable/unprepare idempotence.

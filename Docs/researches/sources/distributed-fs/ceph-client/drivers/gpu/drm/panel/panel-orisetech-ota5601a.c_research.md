# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-orisetech-ota5601a.c

Purpose: SPI/regmap DRM DPI panel driver for Orisetech OTA5601A controllers, currently used for FocalTech GPT3-compatible 640x480 panels.

Important APIs, types, and functions: `struct ota5601a_panel_info` defines mode table, dimensions, bus format, and bus flags. `struct ota5601a` stores the DRM panel, regmap, regulator, panel info, and reset GPIO. Major functions are `ota5601a_probe()`, `ota5601a_prepare()`, `ota5601a_enable()`, `ota5601a_disable()`, `ota5601a_unprepare()`, and `ota5601a_get_modes()`.

Control flow: probe obtains panel info from the SPI device ID table, gets the `power` regulator and reset GPIO, configures SPI mode 3 3-wire, creates an 8-bit regmap, binds OF backlight, and adds the panel. Prepare enables power, applies reset timing, writes the register initialization table, and waits 120 ms. Enable writes `OTA5601A_CTL_ON`; disable writes `OTA5601A_CTL_OFF`; unprepare asserts reset and disables the regulator. Get-modes exports both 60 Hz and 50 Hz 640x480 timings and display bus metadata.

State and persistence: no persistent software state. Register programming is reapplied during prepare; regmap stores only volatile in-memory transaction state.

Dependencies and integration points: SPI core, regmap, regulator, GPIO, DRM panel, media bus format, and OF/SPI matching. Compatible is `focaltech,gpt3`, with SPI ID `gpt3`.

Risks and test signals: OF matching supplies no `.data`, so the driver depends on SPI ID data being available; platforms relying only on OF modalias behavior need confirmation. Remove calls disable and unprepare after removing the panel. SPI 3-wire support and timing values are hardware-sensitive. Test SPI ID matching, register init failures, 50/60 Hz mode export, backlight delay, bus flags, reset polarity, and power-off cleanup.

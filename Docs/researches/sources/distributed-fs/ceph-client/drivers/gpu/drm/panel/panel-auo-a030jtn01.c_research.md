# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-auo-a030jtn01.c

Purpose: SPI/regmap DRM panel driver for AU Optronics A030JTN01 320x480 DPI LCD panels.

Important APIs/types/functions: Defines register masks for standby and blanking, `struct a030jtn01_info`, `struct a030jtn01`, prepare/unprepare/enable/disable/get_modes funcs, regmap readability helper, SPI probe/remove, and match tables.

Control flow: Probe sets SPI mode 3 and 3-wire, allocates a DPI panel, initializes regmap with readable/writeable register mask, obtains match data, regulator, reset GPIO, and optional backlight. Prepare enables power, toggles reset, performs a required dummy register read, programs vertical and horizontal blanking, and leaves the panel ready. Enable sets standby bit and waits for stability; disable clears it. `get_modes` exposes 60 Hz and 50 Hz modes plus RGB888 delta bus format.

State and persistence: Holds SPI, regmap, fixed panel info, regulator, reset GPIO, and optional backlight. Hardware registers are restored on each prepare.

Dependencies and integration: Depends on SPI, REGMAP_SPI, regulator/GPIO, DRM panel, media bus formats, and SPI/OF match data.

Risks: The unexplained dummy read is required for correct colors, so removing it can regress hardware. The register mask limits accessible registers. Two modes are exposed without a preferred bit because `num_modes != 1`.

Test signals: SPI 3-wire communication, dummy-read behavior on real hardware, blanking register writes, both mode timings, standby enable/disable, and power/reset failure cleanup.

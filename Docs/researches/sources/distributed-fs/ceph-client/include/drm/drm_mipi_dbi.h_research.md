# sources/distributed-fs/ceph-client/include/drm/drm_mipi_dbi.h

Purpose: declares helper infrastructure for small MIPI DBI/SPI display controllers, combining bus command helpers, a simple DRM device container, framebuffer conversion/copy support, and ready-made plane/CRTC/connector/mode-config helper vtables.

Important APIs and types: `struct mipi_dbi` stores the command lock, bus-specific command callback, readable command table, byte-swap flag, reset GPIO, and Type-C SPI fields such as D/C GPIO, 9-bit conversion buffer, and write-memory bits-per-word. `struct mipi_dbi_dev` embeds `drm_device`, fixed mode, native pixel format, transfer buffer, rotation, controller offsets, optional backlight/regulators, the DBI interface, and driver-private data. Functions initialize SPI and DRM DBI devices, perform hardware/power-on resets, test display-on state, calculate SPI command speed, transfer SPI buffers, read/write commands, copy framebuffer clips, and initialize debugfs.

Control flow: a tiny-panel driver initializes the SPI-backed DBI bus, initializes `mipi_dbi_dev` with a fixed mode and transfer buffer, registers simple DRM plane/CRTC/connector helpers, then sends MIPI DCS commands via `mipi_dbi_command()` or lower-level buffer helpers. Atomic plane updates copy damaged framebuffer regions into the 16-bit TX buffer and transmit write-memory commands.

State and persistence behavior: command serialization is protected by `cmdlock`. TX buffers, GPIO/regulator/backlight pointers, offsets, rotation, and fixed mode live for the DRM device lifetime. Debugfs is optional under `CONFIG_DEBUG_FS`.

Dependencies and integration points: integrates with SPI, GPIO, regulators, backlight, DRM atomic helpers, GEM shadow framebuffer helpers, format conversion, probe helpers, and MIPI DCS command definitions.

Risks: SPI controllers vary in bits-per-word and max-speed behavior; 9-bit emulation and byte swapping must match panel requirements. Command helpers assume `dbi->spi` is present for error logging. Framebuffer clip copying must respect format, pitch, rotation, offsets, and buffer size. Power/reset sequencing is panel-specific despite common helpers.

Test signals: SPI command/read paths, reset and conditional reset sequencing, RGB565/XRGB8888 framebuffer updates, byte-swap behavior, dirty rectangle clipping, regulator/backlight enable/disable, debugfs command access, and atomic mode validation against the fixed panel mode.

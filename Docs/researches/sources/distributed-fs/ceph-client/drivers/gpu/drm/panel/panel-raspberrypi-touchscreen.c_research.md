# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raspberrypi-touchscreen.c

Purpose: Raspberry Pi 7-inch touchscreen panel driver. The hardware combines a DPI LCD, Toshiba TC358762 DSI-to-DPI bridge, and I2C Atmel ATTINY88 microcontroller; the driver presents a DRM DSI panel while coordinating both I2C power/PWM and a synthetic DSI device.

Important APIs, types, and functions: `struct rpi_touchscreen` holds the DRM panel, DSI device, and I2C client. Register defines cover ATTINY I2C registers and Toshiba bridge DSI/PPI/LCDC registers. Key functions are I2C read/write helpers, `rpi_touchscreen_write()` for generic DSI bridge writes, panel prepare/enable/disable/get-modes, I2C probe/remove, `rpi_touchscreen_dsi_probe()`, and custom module init/exit registering both drivers.

Control flow: I2C probe allocates the panel, validates ATTINY firmware ID, powers the panel off, discovers the DSI host via OF graph, registers a DSI child device named `rpi-ts-dsi`, then adds the panel. The DSI driver probe configures one-lane RGB888 video sync-pulse LPM and attaches. Prepare powers on through I2C, polls `REG_PORTB`, programs TC358762 bridge registers over generic DSI writes, and starts PPI/DSI. Enable sets PWM to 255 and default horizontal flip. Disable sets PWM and power off.

State and persistence: no persisted software state. Hardware microcontroller and bridge registers hold volatile configuration after prepare.

Dependencies and integration points: I2C/SMBus, OF graph, MIPI DSI host/device registration, DRM panel, media bus format, and module lifecycle. Compatible string is `raspberrypi,7inch-touchscreen-panel`; DSI child driver name is `rpi-ts-dsi`.

Risks and test signals: the power-on poll has no delay and no timeout error if the bit never appears; DSI generic writes ignore return values. Remove detaches and unregisters the synthetic DSI device. Test firmware revision detection, graph probe deferral, DSI child attach, bridge register programming, PWM/backlight behavior, mode 800x480 export, and remove ordering.

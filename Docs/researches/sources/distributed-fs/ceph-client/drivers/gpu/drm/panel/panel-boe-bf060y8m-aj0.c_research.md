# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-bf060y8m-aj0.c

Purpose: MIPI DSI OLED panel driver for the BOE BF060Y8M-AJ0 5.99 inch 1080x2160 module using an SW43404-like controller.

Important APIs/types/functions: Defines supply enum, `struct boe_bf060y8m_aj0`, reset/on/off helpers, prepare/unprepare, fixed mode, DCS backlight ops, regulator initialization, DSI probe/remove, and OF match table.

Control flow: Probe validates and obtains five supplies, optional reset GPIO, configures four-lane RGB888 video sync-pulse DSI, marks `prepare_prev_first`, creates a DCS backlight, registers the panel, and attaches. Prepare enables ELVDD/ELVSS first, then VCC/VDDIO/VCI with delays, toggles reset, and sends DCS init/sleep-out/display-on. Unprepare sends display-off/sleep-in in high-speed mode, asserts reset, and bulk-disables supplies. Backlight writes DCS brightness.

State and persistence: State stores DSI, regulators, reset GPIO, and DRM panel/backlight. Supply voltage/current constraints are checked/set at probe but not persisted by this driver beyond regulator framework state.

Dependencies and integration: Depends on MIPI DSI, backlight class, regulator framework, GPIO, DRM panel, and video MIPI DCS definitions.

Risks: Power sequence is strict and uses negative ELVSS represented as positive regulator voltage magnitude. `regulator_is_supported_voltage` returning zero is treated as failure, which assumes unsupported ranges are fatal. Optional reset GPIO is still used unconditionally in reset/off paths if absent, relying on gpiod handling NULL safely.

Test signals: Regulator constraint handling, ordered power-up/down with delays, DSI command success, DCS brightness, fixed mode at 1080x2160, and failure cleanup after each supply or DSI step.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-raydium-rm69380.c

Purpose: DRM MIPI-DSI driver for Raydium RM69380-equipped Lenovo J716F EDO panels, supporting optional dual-DSI attachment and a 2560x1600 90 Hz mode.

Important APIs, types, and functions: `struct rm69380_panel` contains DRM panel, two possible DSI links, two regulators (`vddio`, `avdd`), and reset GPIO. Main functions are `rm69380_probe()`, `rm69380_prepare()`, `rm69380_unprepare()`, `rm69380_on()`, `rm69380_off()`, `rm69380_get_modes()`, and DCS large-brightness backlight ops.

Control flow: probe allocates state, gets supplies and reset GPIO, checks OF graph port 1 for a secondary DSI host and registers a second DSI device when present, sets drvdata on DSI links, marks `prepare_prev_first`, creates a raw DCS backlight, adds the panel, then iterates over existing DSI links to configure four-lane RGB888 burst/non-continuous flags and attach. Prepare enables both supplies, resets, sends DCS page commands on DSI0, enables LPM on both links, exits sleep, and turns display on. Unprepare sends display-off/sleep through DSI0, asserts reset, and disables regulators.

State and persistence: no persistent state. Runtime state is the two-element DSI array and DSI mode flags on both links. Brightness operations act on the primary DSI link.

Dependencies and integration points: DRM panel, MIPI DSI, OF graph, regulator bulk, GPIO, fixed-mode helper, and backlight. Compatible string is `lenovo,j716f-edo-rm69380`.

Risks and test signals: command traffic is only sent through primary DSI, so dual-link panel synchronization depends on host/panel behavior. Attach loop removes the panel on attach failure. The module author string appears to miss a closing quote character in the literal content. Test single-link and dual-link DT graphs, secondary host deferral, brightness, fixed 90 Hz mode, regulator rollback, attach failure, and suspend/resume.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-tv101wum-nl6.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-tv101wum-nl6.c

### Purpose

`panel-boe-tv101wum-nl6.c` is a MIPI-DSI DRM panel driver for a family of 10.1-11 inch 1200x1920 or 1200x2000 video-mode panels using related BOE, AUO, Innolux, and Starry modules. The file is table driven: each compatible selects a `panel_desc` that supplies the display mode, DSI lane/format/mode flags, physical size, bpc, power sequencing quirks, and a panel-specific DCS initialization routine.

### Important APIs, types, and functions

The central types are `struct panel_desc` and `struct boe_panel`. `panel_desc` stores the fixed `drm_display_mode`, DSI bus parameters, init callback, and quirks such as `discharge_on_disable` and `lp11_before_reset`. `boe_panel` holds the `drm_panel`, DSI device, orientation, four regulators (`pp3300`, `pp1800`, `avdd`, `avee`), and the enable/reset GPIO.

Panel-specific init functions include `boe_tv110c9m_init()`, `inx_hj110iz_init()`, `boe_init()`, `auo_kd101n80_45na_init()`, `auo_b101uan08_3_init()`, and `starry_qfh032011_53g_init()`. `boe_init()` is the common long register sequence used by the BOE TV101WUM variants. The DRM callbacks are `boe_panel_prepare()`, `boe_panel_enable()`, `boe_panel_disable()`, `boe_panel_unprepare()`, `boe_panel_get_modes()`, and `boe_panel_get_orientation()`. Device registration is handled by `boe_panel_probe()`, `boe_panel_add()`, `boe_panel_remove()`, and `module_mipi_dsi_driver()`.

### Control flow

Probe allocates the `boe_panel`, reads match data from `boe_of_match`, applies DSI lane/format/mode flags from the descriptor, obtains the four regulators, gets the `enable` GPIO, reads panel orientation, registers optional backlight support, adds the DRM panel, and attaches to the DSI host. `prepare()` powers rails in order (`pp3300`, `pp1800`, `avdd`, `avee`), optionally sends a DSI NOP before reset to force LP11, toggles the enable GPIO through the panel reset sequence, then calls the descriptor-specific init callback. The init callbacks write vendor command pages, gamma tables, GOA/source timing values, sleep-out/display-on commands, or simple `0x11`/`0x29` sequences depending on the panel. `enable()` only waits 130 ms after init; the panel is already commanded on by the init path. `disable()` sends display-off and sleep-in around LPM flag handling, and `unprepare()` turns off GPIO and rails with either normal or discharge-oriented ordering.

### State and persistence behavior

Runtime state is device-local and not persisted outside the kernel object. The selected descriptor is immutable match data. Power state is represented implicitly by the regulator/GPIO state and DRM panel prepare/enable lifecycle rather than by explicit booleans. Orientation comes from device tree and is returned through both `get_orientation()` and the legacy connector orientation call in `get_modes()`. DSI mode flags are mutated during disable to leave low-power mode enabled after sleep-in. The long vendor register sequences program panel IC state until the next reset or power loss.

### Dependencies

The driver depends on DRM panel and connector helpers, MIPI DSI DCS helpers including `mipi_dsi_multi_context`, OF match data, regulator and GPIO consumer APIs, `drm_panel_of_backlight()`, and `of_drm_get_panel_orientation()`. It integrates with the MIPI DSI bus through `struct mipi_dsi_driver` and with the DRM display pipeline through `struct drm_panel_funcs`.

### Integration points

Supported compatibles are `boe,tv101wum-nl6`, `auo,kd101n80-45na`, `boe,tv101wum-n53`, `auo,b101uan08.3`, `boe,tv105wum-nw0`, `boe,tv110c9m-ll3`, `innolux,hj110iz-01a`, and `starry,2081101qfh032011-53g`. Board DTS must provide the named regulators, enable GPIO, optional backlight, and orientation. The DSI host uses descriptor-supplied video-mode flags, usually four lanes and RGB888. Connectors receive one fixed preferred mode plus physical size and bpc.

### Risks

The highest risk is sequencing: panel rails, LP11-before-reset, reset timing, and discharge ordering are panel-specific and easy to break when adding variants. Error unwinding in `boe_panel_prepare()` disables `avee`, `avdd`, and `pp1800` but does not disable `pp3300`, so failures after the first rail may leave one supply enabled until later cleanup. Init callbacks return `0` directly instead of `ctx.accum_err`, so accumulated DSI write failures are not propagated for these sequences. The descriptor table must stay consistent with DSI host capabilities, because wrong mode flags, lane count, or timings can produce blank panels or unstable links.

### Test signals

Useful validation includes kernel build coverage with `CONFIG_DRM_PANEL_BOE_TV101WUM_NL6`, probe/remove on each compatible, regulator/GPIO trace checks for prepare and unprepare order, DSI host logs for attach and command failures, visual bring-up through sleep-out/display-on, suspend/resume and blank/unblank cycles, orientation reporting, backlight binding, and mode enumeration confirming the expected resolution, bpc, and physical dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-tv101wum-nl6.c -->

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm_lcd.h

Purpose: declares the LCD-specific DMUB ABM helper surface used by the higher-level DMUB ABM wrapper.

Important APIs: initialization and query functions are `dmub_abm_init()`, `dmub_abm_get_current_backlight()`, and `dmub_abm_get_target_backlight()`. Control functions include `dmub_abm_set_level()`, `dmub_abm_init_config()`, `dmub_abm_set_pause()`, `dmub_abm_save_restore()`, `dmub_abm_set_pipe()`, `dmub_abm_set_backlight_level()`, and `dmub_abm_set_event()`.

Control flow role: callers pass a generic `struct abm *` plus panel or pipe identifiers. The implementation converts to `struct dce_abm` for register access and sends DMUB ABM commands for firmware-owned behavior.

State and persistence: the header forward-declares `struct abm_save_restore`, which is the caller-owned persistence payload used by firmware save/restore exchange. Backlight values are documented in implementation as 17-bit u1.16 hardware format.

Dependencies and integration: includes `abm.h` and relies on `dc_context`, DMUB command structs, and DCE ABM descriptors through the implementation. It is integrated by `dmub_abm.c`, not usually by generic callers directly.

Risks and test signals: because this is a low-level command API, callers must supply valid panel instances, panel masks, config byte counts, and scratch-compatible buffers. Test coverage should compile the prototypes against `dmub_abm.c`, exercise each command subtype, and validate save/restore buffer contents after firmware completion.

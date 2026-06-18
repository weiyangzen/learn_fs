# sources/distributed-fs/ceph-client/drivers/input/mouse/logips2pp.c

`logips2pp.c` implements Logitech PS/2++ and PS2T++ extensions. It detects Logitech model/button information, enables extended packets where supported, maps model-table features to input capabilities, decodes extra wheel/button packets, supports optional 800 dpi resolution, and exposes a SmartScroll sysfs control.

Important functions are `ps2pp_detect()`, `get_model_info()`, `ps2pp_cmd()`, `ps2pp_process_byte()`, `ps2pp_set_model_properties()`, `ps2pp_setup_protocol()`, and SmartScroll handlers. Detection sends Logitech query/magic sequences, uses a model table, performs a special TouchPad 3 setup path, and either installs the PS2++ handler or returns `-ENXIO` so psmouse can continue probing.

State lives mainly in `struct psmouse`: model, name/vendor, `smartscroll`, callbacks, and packet size. Dependencies are psmouse helpers, libps2 sliced commands, input, and sysfs attributes. Risks are unknown model fallback, device-specific command sequences, extended packet subtype gaps, and SmartScroll/800 dpi behavior varying by hardware. Test signals include model capabilities, extended packet decoding, sysfs lifecycle, fallback to standard PS/2, and resolution behavior.

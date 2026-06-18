# sources/distributed-fs/ceph-client/drivers/input/mouse/logips2pp.h

`logips2pp.h` is the minimal Logitech PS/2++ header. It declares `ps2pp_detect(struct psmouse *psmouse, bool set_properties)` for the psmouse protocol table.

The detector is both identification and optional setup entry point. The header defines no state; runtime state is kept in `psmouse` and sysfs files created by `logips2pp.c`.

Integration depends on Kconfig guarding the psmouse table reference. Risks are signature/table mismatch or missing Kconfig guard. Test signals are build coverage with Logitech PS2++ enabled and disabled.

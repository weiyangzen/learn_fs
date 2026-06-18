<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-pxrc.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-pxrc.c

## Purpose
This driver supports the PhoenixRC 8-axis flight controller by replacing the broken device report descriptor with a fixed joystick descriptor and rewriting alternating raw reports so the shared last byte becomes stable slider and dial axes.

## Important APIs, types, and functions
`struct pxrc_priv` stores cached slider, cached dial, and an `alternate` toggle. `pxrc_rdesc_fixed` is the replacement HID descriptor declaring a joystick with X, Slider, Y, Z, Rx, Ry, Rz, and Dial axes, all 8-bit absolute values. `pxrc_report_fixup` unconditionally replaces the descriptor. `pxrc_raw_event` rewrites report bytes using the cached alternating values. `pxrc_probe` allocates private state, parses, and starts hardware.

## Control flow
During parse, `pxrc_report_fixup` sets `*rsize` to the fixed descriptor length and returns the static descriptor. Probe stores zeroed private state in HID drvdata, parses the fixed descriptor, then starts HID normally. Each raw event alternates interpretation of `data[7]`: on one report it updates `dial`, on the next it updates `slider`. It then writes the cached slider to `data[1]` and cached dial to `data[7]`, toggles `alternate`, and allows generic HID input handling to continue.

## State and persistence behavior
Only the previous slider/dial values and the alternation bit persist between reports. They are reset on reconnect. There is no sysfs or device memory state.

## Dependencies and integration points
The file integrates with HID report descriptor fixup and raw-event mutation before generic joystick input processing. It depends on `hid-ids.h` for the PhoenixRC USB ID.

## Risks and test signals
Risks are unconditional descriptor replacement and reliance on strict report alternation. Dropped or reordered reports can temporarily pair stale slider/dial values. Tests should inspect the exposed eight axes, feed alternating raw reports, verify slider/dial stability, reconnect reset behavior, and generic joystick calibration in userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-pxrc.c -->

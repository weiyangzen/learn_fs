<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/regulator.h

## Purpose
`regulator.h` is the WM831x regulator and current-sink register map. It defines enables, status/fault bits, DCDC/LDO operating modes, voltage selectors, startup/shutdown slots, sleep settings, hardware-control selectors, dynamic-voltage-scaling selectors, power-good sources, and current-sink selector data.

## Important APIs, types, and functions
The only symbol declaration is `extern const unsigned int wm831x_isinkv_values[WM831X_ISINK_MAX_ISEL + 1]`, with `WM831X_ISINK_MAX_ISEL` set to 55. Macro groups cover current sinks `CS1/CS2`, DCDC enable/status/UV/OV/HC registers, LDO enable/status/UV registers, DC1/DC2 BuckWise controls with DVS fields, DC3/DC4 controls, LDO1-LDO10 control/on/sleep fields, LDO11 on/sleep fields, and power-good source bits for DC and LDO rails.

## Control flow
Regulator drivers translate regulator framework operations into register updates: enable bits in aggregate registers, voltage selectors in ON/SLEEP/DVS registers, mode and hardware-control fields in per-rail control registers, and status/fault reads for `is_enabled`, error reporting, or IRQ handling.

## State and persistence behavior
Rail state lives in hardware registers and includes active/sleep voltage images, hardware-control source/mode, dynamic voltage state, current-sink drive/ramp/current, power-good state, and fault latches. Some values are board policy and should be restored after reset or resume.

## Dependencies and integration points
This header is consumed by WM831x regulator, LED/backlight current-sink, PMU, IRQ, and platform-data code. It is tied to Linux regulator constraints and to IRQ definitions for UV/high-current/current-sink events.

## Risks and test signals
Risks include rail-index/register mismatches, invalid voltage selector tables, ignoring LDO11's distinct 4-bit selector format, DVS source misconfiguration, and missed fault handling. Test signals include regulator list-voltage/set-voltage tests, enable/status readback, suspend mode restoration, DVS GPIO transitions, current-sink brightness tables, and UV/HC fault IRQ injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/regulator.h -->

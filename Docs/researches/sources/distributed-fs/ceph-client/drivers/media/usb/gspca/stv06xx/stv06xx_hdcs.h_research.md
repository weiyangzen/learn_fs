# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_hdcs.h

Purpose: defines HDCS sensor register constants, defaults, static init tables, function prototypes, and the two STV06xx sensor descriptors for HDCS-1000/1100 and HDCS-1020.

Important APIs and types: key macros include HDCS register selectors, `HDCS_REG_CONFIG`, `HDCS_REG_CONTROL`, default dimensions, clock/exposure constants, run/sleep bits, and default exposure/gain. It defines `stv06xx_sensor_hdcs1x00` and `stv06xx_sensor_hdcs1020` with I2C address, byte length, packet sizes, and operation callbacks.

Control flow: `stv06xx.c` references the descriptor symbols during sensor probing. `stv06xx_hdcs.c` consumes the register definitions and init arrays to reset, configure, start, stop, and dump sensors.

State and persistence: no runtime state is allocated here; descriptor objects and init arrays are static module data.

Dependencies and integration points: depends on `stv06xx_sensor.h` and the shared `IS_1020(sd)` macro. The descriptor objects are defined in the header as part of the local single-inclusion backend pattern.

Risks: defining `const` objects in a header would cause duplicate definitions if included from multiple translation units. Fixed packet-size descriptors have FIXME comments about bandwidth and framerate testing. Register addresses are left-shifted because low bit encodes read/write, which is easy to misuse.

Test signals: compile/link of the composite module, probe ID-specific descriptors, verify packet size negotiation, and compare sensor register dump output with expected HDCS datasheets/traces.

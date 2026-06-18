# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_pb0100.h

Purpose: declares PB-0100 sensor register constants, mode flag bits, local backend prototypes, control helper prototypes, and the `stv06xx_sensor_pb0100` descriptor.

Important APIs and types: macros cover chip ID, windowing, blanking, control, exposure, gain, DAC, thresholds, ADC, and chip-enable registers. Mode flags are `PB0100_CROP_TO_VGA` and `PB0100_SUBSAMPLE`. The descriptor sets I2C flush/address/word length, packet sizes, and callbacks.

Control flow: included by `stv06xx_pb0100.c`, this header supplies constants for all register writes and gives `stv06xx.c` access to the sensor descriptor via `stv06xx_sensor.h` extern declarations.

State and persistence: contains static descriptor data and compile-time constants only; runtime control state is allocated in the C file.

Dependencies and integration points: depends on `stv06xx_sensor.h` and the single composite module build pattern.

Risks: the descriptor object is defined in the header, so multiple inclusion outside the current pattern would duplicate symbols. Many registers are reserved or lightly documented, making misuse easy. Packet-size arrays cover only the advertised modes.

Test signals: compile/link of the PB0100 backend, probe matching ID, check descriptor packet sizes during iso negotiation, and verify register writes from controls against expected PB0100 behavior.

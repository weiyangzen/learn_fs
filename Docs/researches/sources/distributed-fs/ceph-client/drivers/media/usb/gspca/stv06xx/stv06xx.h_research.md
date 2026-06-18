# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx.h

Purpose: defines the common STV06xx bridge register map, I2C command-buffer constants, LED constants, bridge enum values, shared `struct sd`, and helper prototypes used by all STV06xx sensor backends.

Important APIs and types: `struct sd` embeds `gspca_dev`, selected `struct stv06xx_sensor`, backend `sensor_priv`, `to_skip`, and bridge type. Macros define ISO, I2C, scan-rate, LED, reset, and axis-control registers plus bridge IDs `BRIDGE_STV600`, `BRIDGE_STV602`, `BRIDGE_STV610`, and `BRIDGE_ST6422`. Prototypes expose bridge and sensor read/write helpers.

Control flow: sensor backends include this header through `stv06xx_sensor.h` and use the helper prototypes to program bridge and sensor registers. The core uses the bridge enum to select protocol quirks and packet skipping.

State and persistence: declares runtime state layout but performs no allocation itself. Values are per-device and freed by `stv06xx.c`.

Dependencies and integration points: depends on `gspca.h`, Linux slab header, and the STV06xx backend contract. It is the central ABI between bridge core and sensor files inside the module.

Risks: `MODULE_NAME` is uppercase `"STV06xx"` while the built module is `gspca_stv06xx`, which can confuse log filtering. Shared `struct sd` changes affect every backend. Fixed I2C buffer sizes limit batching assumptions.

Test signals: compile all backends, validate bridge register constants against USB traces, and run streaming tests for each bridge enum path.

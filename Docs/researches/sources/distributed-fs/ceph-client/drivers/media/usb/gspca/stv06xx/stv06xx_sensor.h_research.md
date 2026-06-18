# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_sensor.h

Purpose: defines the common sensor-backend interface used by the STV06xx bridge core and declares the linked sensor descriptor objects.

Important APIs and types: `struct stv06xx_sensor` contains sensor name, I2C address/flush/word length, per-mode min/max packet sizes, and callbacks for probe, init, controls, direct read/write hooks, start, stop, and dump. Extern descriptors include VV6410, HDCS1x00, HDCS1020, PB0100, and ST6422. `IS_1020(sd)` distinguishes the HDCS1020 descriptor.

Control flow: `stv06xx.c` iterates descriptor objects and calls their callbacks through this interface. Backends fill mode tables and private state during probe, then use callbacks for lifecycle and controls.

State and persistence: the header defines no mutable state itself. It describes static descriptors and callback contracts.

Dependencies and integration points: includes `stv06xx.h`, creating a circular-looking but guarded contract between shared device state and sensor descriptors.

Risks: callback semantics are convention-based; not all backends implement optional direct read/write hooks. Packet-size arrays have fixed length four and must match backend mode counts. `IS_1020` compares descriptor addresses, so duplicate descriptor definitions would break identity tests.

Test signals: compile all backends, verify each descriptor probe path, exercise core delegation for init/control/start/stop/dump, and check packet-size arrays against mode tables.

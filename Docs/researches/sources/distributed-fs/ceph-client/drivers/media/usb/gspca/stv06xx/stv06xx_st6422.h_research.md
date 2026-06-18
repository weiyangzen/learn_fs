# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_st6422.h

Purpose: declares the ST6422 backend callbacks and defines the `stv06xx_sensor_st6422` descriptor for the integrated sensor variant.

Important APIs and types: prototypes include `st6422_probe`, `st6422_start`, `st6422_init`, `st6422_init_controls`, and `st6422_stop`. The descriptor names the sensor, supplies fixed min/max packet sizes `{300, 847}`, and assigns lifecycle callbacks.

Control flow: the STV06xx core tries this descriptor first; its probe succeeds only for `BRIDGE_ST6422`, avoiding I2C probing for integrated hardware.

State and persistence: no runtime state in the header; static descriptor data only.

Dependencies and integration points: depends on `stv06xx_sensor.h` and the composite-module single-definition pattern.

Risks: descriptor definition in a header is fragile if included by more than one translation unit. Packet-size comments say no known framerate lowering exists, so bandwidth fallback is limited.

Test signals: compile/link, ST6422 probe success/failure by bridge type, and iso negotiation using fixed packet sizes.

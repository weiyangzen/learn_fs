# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx.c

Purpose: implements the common STV06xx GSPCA bridge driver that probes sensor backends, provides bridge/sensor I2C helpers, starts/stops isochronous streaming, parses chunked USB packets, and handles optional camera-button input.

Important APIs and functions: exported-in-module helpers are `stv06xx_write_bridge`, `stv06xx_read_bridge`, `stv06xx_write_sensor`, `stv06xx_write_sensor_bytes`, `stv06xx_write_sensor_words`, and `stv06xx_read_sensor`. GSPCA hooks include `stv06xx_config`, `stv06xx_init`, `stv06xx_init_controls`, `stv06xx_start`, `stv06xx_stopN`, `stv06xx_pkt_scan`, `stv06xx_isoc_init`, `stv06xx_isoc_nego`, `sd_int_pkt_scan`, `stv06xx_probe_error`, and custom disconnect cleanup.

Control flow: config records bridge type from USB `driver_info`, optionally dumps bridge registers, and probes sensors in order: ST6422, VV6410, HDCS1x00, HDCS1020, PB0100. Init delays for USB settle and delegates to the selected sensor. Control init delegates to the sensor. Start finds the selected altsetting endpoint size, writes it to bridge registers, starts the sensor, and enables ISO streaming. Iso negotiation reduces packet size by 100 down to the sensor minimum and retries altsetting selection. Packet scan walks chunked packets with id/length headers, maps SOF/EOF/data chunks to GSPCA packets, skips first corrupt ST6422 lines, and discards malformed chunks.

State and persistence: `struct sd` in `stv06xx.h` stores selected sensor, sensor-private pointer, ST6422 skip counter, and bridge type. Sensor-private memory is freed on probe error and disconnect. All state is volatile per device.

Dependencies and integration points: depends on GSPCA, USB vendor control transfers, optional input support, `stv06xx_sensor.h`, and all sensor backend descriptors linked into the module. USB IDs identify STV600, STV610, STV602, and ST6422 bridge variants.

Risks: sensor probing relies on ordered fallbacks and shared `sensor_priv` ownership. I2C command batching depends on fixed buffer layout and sensor `i2c_len`. Packet parsing trusts chunk length after bounds checks but unknown chunks are skipped silently. Iso negotiation mutates endpoint descriptor packet size in the active config cache. Debug dump mode writes test values to bridge registers and restores them, which is risky on hardware.

Test signals: build `gspca_stv06xx`, probe each USB ID/bridge generation, verify sensor detection order, stream each backend, exercise bandwidth fallback, test input interrupt packets, malformed chunk handling, suspend/resume, and disconnect memory cleanup.

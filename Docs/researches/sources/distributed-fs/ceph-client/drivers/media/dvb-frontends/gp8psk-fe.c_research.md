# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/gp8psk-fe.c

### Purpose
`gp8psk-fe.c` implements the frontend layer for Genpix USB DVB-S/Turbo-FEC/8PSK receivers. It translates DVB frontend operations into device-specific USB control operations supplied by a parent driver.

### Important APIs, Types, And Functions
`struct gp8psk_fe_state` stores the embedded frontend, parent private pointer, command ops, revision flag, cached lock/SNR, and status polling interval. `gp8psk_fe_attach()` is exported and requires `in`, `out`, and `reload` callbacks. Key callbacks include `gp8psk_fe_set_frontend()`, `gp8psk_fe_read_status()`, `gp8psk_fe_read_snr()`, signal strength mapping, DiSEqC/tone/voltage control, high LNB voltage, and legacy Dish Network command support.

### Control Flow
Set-frontend packs symbol rate and frequency into a 10-byte command buffer, normalizes DVB-S plus PSK_8 into `SYS_TURBO`, validates modulation and delivery system, maps FEC values to firmware fields, optionally reloads revision-1 firmware when leaving DCII mode, sends `TUNE_8PSK`, and resets cached status polling. Status reads are rate-limited with `jiffies`; unlocked state polls every 100 ms and locked state every 1000 ms.

### State, Persistence, And Dependencies
Driver state is memory-only; device state is controlled by parent `gp8psk_fe_ops` commands. Cached `lock` and `snr` reduce USB traffic. It depends on Genpix command constants from the header, DVB frontend cache fields, module debug parameter, and parent USB transport.

### Integration Points
The parent USB driver supplies command callbacks and receives all hardware I/O. The frontend advertises DVB-S caps with Turbo-FEC compatibility and provides satellite SEC controls.

### Risks
Many `ops->in/out` return values are ignored, especially status polling and tune command completion. DiSEqC burst comments admit likely-wrong commands. `set_voltage()` maps any non-18V value to false, including OFF and invalid enum values. DVB-S2 is accepted only for backward compatibility without distinct command mapping.

### Test Signals
Test revision-1 reload paths, QPSK/8PSK/16QAM FEC mapping, unsupported modulation errors, status polling cadence, SNR-to-strength scaling, DiSEqC/tone/voltage USB commands, and parent callback failure propagation.

# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u-fe.c

Purpose: custom DVB-T frontend implementation for WideView/Yakumo/Hama/Typhoon/Yuan DTT200U-style devices whose demodulator control is exposed through simple USB firmware commands rather than a normal demod driver.

Important APIs/types/functions: `struct dtt200u_fe_state` stores device pointer, cached status/properties, embedded `struct dvb_frontend`, an 80-byte command buffer, and a mutex. `dtt200u_fe_attach()` allocates and returns the frontend. Frontend ops implement init/sleep, set/get frontend, tune settings, status, BER, signal strength, SNR, uncorrected blocks, and release.

Control flow: read callbacks lock `data_mutex`, place a GET command byte in `data[0]`, call `dvb_usb_generic_rw()`, decode the returned bytes, and unlock. `set_frontend()` validates bandwidth, writes `SET_BANDWIDTH`, converts frequency to 250 kHz units, then writes `SET_RF_FREQ`. `get_tune_settings()` requires a 1500 ms delay. Attach initializes state, copies `dtt200u_fe_ops`, and stores the private pointer.

State and persistence: frontend state persists in allocated memory until `release`. Firmware maintains tune status, signal counters, bandwidth, and RF frequency. The local `fep` cache is returned by `get_frontend()` but is not updated by `set_frontend()` in this file, so it is only a local snapshot.

Dependencies and integration: used by `dtt200u.c`; depends on generic DVB USB bulk control and DVB frontend core.

Risks: all command traffic shares one mutable buffer, so mutex coverage is critical. Unknown tune status maps to no lock. `get_frontend()` returns cached state that may be stale. Frequency division assumes firmware wants 250 kHz units and ignores unsupported bandwidths.

Test signals: frontend attach/release, tune requests for 6/7/8 MHz, lock and timeout status transitions, BER/SNR/AGC/uncorrected block reads, invalid bandwidth rejection, and repeated open/close under USB error injection.

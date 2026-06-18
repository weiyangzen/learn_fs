# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dtt200u.c

Purpose: DVB USB driver for WideView/Yakumo/Hama/Typhoon/Yuan/Miglia WT200U/WT220U-style USB2 DVB-T receivers. It implements firmware commands for power, streaming, PID filtering, rc-core remote handling, device profiles, and USB registration.

Important APIs/functions: `dtt200u_power_ctrl()`, `dtt200u_streaming_ctrl()`, `dtt200u_pid_filter()`, `dtt200u_rc_query()`, `dtt200u_frontend_attach()`, and `dtt200u_usb_probe()` are the active callbacks. Property blocks cover DTT200U, WT220U, Freecom endpoint variant, ZL353 variant, and Miglia firmware-only transition.

Control flow: probe tries each property profile through `dvb_usb_device_init()`. Power-on writes `SET_INIT`. Streaming writes `SET_STREAMING` and, on stop, resets the PID table. PID filter writes index and 13-bit PID, or zero when disabled. RC query reads five bytes, decodes NEC/NECX scancodes with checksum validation, and reports keydown/repeat/keyup via rc-core. Frontend attach delegates to `dtt200u_fe_attach()`.

State and persistence: `struct dtt200u_state` contains an 80-byte data buffer protected by the device data mutex. Firmware state persists power initialization, streaming enable, PID table, RC buffer, and frontend tuning state.

Dependencies and integration: depends on `dtt200u-fe.c`, `dtt200u.h`, DVB USB core, rc-core, and Cypress FX2 firmware loading. It uses generic bulk endpoint `0x01` for commands and endpoint `0x02` or `0x06` for MPEG-TS.

Risks: several property initializers are visually misindented, so future edits can easily place fields at the wrong nesting level. Miglia profile has no adapter/frontend because it changes USB ID after firmware upload. RC checksum failures intentionally key up, which may hide noisy packets. PID table reset only happens on stream stop.

Test signals: cold/warm probe for every USB ID, firmware names, endpoint-specific streaming, PID filter count 15 behavior, NEC and NECX remote events, frontend tune/status commands, and firmware-only Miglia reconnect behavior.

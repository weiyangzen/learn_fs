# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/vp702x-fe.c

## Purpose
This file implements the custom DVB-S frontend operations for Twinhan VP7020/VP7021 StarBox devices, where much frontend control is hidden behind firmware commands rather than standard demod/tuner drivers.

## Important APIs, types, and functions
`struct vp702x_fe_state` embeds `struct dvb_frontend`, stores the USB device, SEC voltage/tone state, LNB command buffer, cached lock/signal/SNR values, and status polling cadence. `vp702x_fe_refresh_state()` reads status and tuner registers. `vp702x_fe_set_frontend()` encodes frequency, symbol rate, voltage flag, and checksum into an 8-byte command. DiSEqC, tone, voltage, metrics, init, release, and tune-settings callbacks populate `vp702x_fe_ops`.

## Control flow and state
Status is rate-limited with `next_status_check`; locked frontends poll slower than unlocked ones. Tuning builds a firmware command using kHz frequency and scaled symbol rate, then sends a USB in/out operation through the parent driver buffer. SEC voltage/tone changes update `lnb_buf`, recompute checksum, and send it through the same command path.

## Dependencies and integration
The file depends on `vp702x.h` for USB helpers, command constants, debug macros, and shared device buffer locking. It returns a software frontend from `vp702x_fe_attach()` for use by `vp702x.c`.

## Risks and test signals
Risks include firmware-specific encoding, limited DiSEqC message length, cached status staleness, implicit lock polarity where `lock == 0` means locked, and shared buffer concurrency. Test tune success/failure, lock acquisition, signal/SNR reads, LNB voltage/tone changes, DiSEqC commands up to four bytes, and frontend release on unplug.

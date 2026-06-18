# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst.c

## Purpose
`dst.c` is the DVB frontend/card driver for TwinHan DST devices attached through bt878 hardware. It implements the private DST/RDC 8820 command protocol over bt878 GPIO-assisted PIO and I2C, identifies the board/firmware/tuner, configures transport packet size, and exposes DVB frontend operations for DVB-S, DVB-T, DVB-C, and ATSC variants.

## Important APIs, Types, And Functions
Exported functions are `rdc_reset_state()`, `dst_pio_disable()`, `dst_wait_dst_ready()`, `dst_error_recovery()`, `dst_error_bailout()`, `dst_comm_init()`, `write_dst()`, `read_dst()`, `dst_check_sum()`, and `dst_attach()`. Core internal paths include `dst_gpio_outb()`, `dst_gpio_inb()`, `rdc_8820_reset()`, `dst_command()`, `dst_probe()`, `dst_get_device_id()`, `dst_write_tuna()`, `dst_get_tuna()`, and DVB ops such as `dst_set_frontend()`, `dst_tune_frontend()`, `dst_read_status()`, `dst_set_voltage()`, `dst_set_tone()`, and `dst_set_diseqc()`.

## Control Flow
`dst_attach()` receives an allocated `struct dst_state`, calls `dst_probe()`, then copies the frontend ops matching detected `dst_type`. Probe optionally resets CA daughterboard hardware, initializes PIO, requests device ID via a fixed 8-byte command, matches firmware strings against `dst_tlist`, discovers tuner type/capabilities, requests MAC/firmware/card/vendor information when supported, and sets TS packet size to 204 when required. Tuning updates `state->tx_tuna` based on delivery system, frequency, symbol rate, bandwidth, modulation, FEC, voltage, tone, and DiSEqC state, then sends it through the DST command protocol and reads back lock/frequency.

## State And Persistence
`struct dst_state` persists frontend state: tx/rx command buffers, detected type flags/features, current frontend properties, DiSEqC/power flags, decode lock/strength/SNR, firmware strings, tuner/card/vendor info, `dst_mutex`, and optional CA device pointer. Hardware state exists in the DST ASIC, bt878 GPIO lines, and TS packet-size control. There is no disk persistence.

## Dependencies And Integration Points
This file depends on Linux DVB frontend APIs, `bt878_device_control()` from the bt878 bridge, I2C transfer APIs, `dst_common.h`/`dst_priv.h`, and optional CA attachment handled by `dst_ca.c` from release cleanup. The frontend is typically instantiated by `dvb-bt8xx`.

## Risks
The communication protocol is timing-sensitive, with sleeps, PIO toggles, ACK bytes, checksum validation, and recovery resets. Device identification falls back to satellite/symdiv defaults for unknown strings, which can misconfigure unsupported hardware. Several board capability paths are firmware-string-specific. Mutex coverage is vital because CA and frontend paths share the same DST command channel. Tuning status is partly cached, so stale lock state is possible if command recovery fails.

## Test Signals
Signals include successful `dst_attach()`, recognized firmware/model logs, TS188/TS204 selection, DVB frontend registration with the correct delivery system, successful tuning/lock for supported satellite/terrestrial/cable/ATSC inputs, valid signal strength/SNR reads, DiSEqC/voltage/tone behavior on satellite cards, and recovery from transient I2C/PIO errors without wedging the frontend.


# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda826x.c

## Purpose
`tda826x.c` implements Philips TDA8262/TDA8263 DVB-S silicon tuners. It attaches tuner ops to an existing frontend, detects tuner presence, programs LO and baseband filter settings based on frequency and symbol rate, supports loop-through power handling, and reports cached tuned frequency.

## Important APIs, Types, and Functions
The exported API is `tda826x_attach()`. `struct tda826x_priv` stores I2C address, adapter, loop-through flag, and cached frequency. Tuner callbacks include `tda826x_sleep()`, `tda826x_set_params()`, `tda826x_get_frequency()`, and `tda826x_release()`.

## Control Flow
Attach opens the frontend I2C gate, performs a zero-length write followed by a two-byte read to detect tuner status bit `0x80`, allocates private state, installs tuner ops, and stores `tuner_priv`. Set-params opens the gate, computes integer MHz divider from requested frequency, computes baseband bandwidth from symbol rate with rolloff assumptions and clamps it to 5 to 36 MHz, writes an 11-byte register block, closes the gate, and caches the rounded frequency. Sleep writes a two-byte powerdown command that differs depending on loop-through presence.

## State and Persistence Behavior
Only volatile tuner private state is stored. The cached frequency is the rounded programmed LO value in kHz. Sleep changes hardware power state but is not persisted across attach.

## Dependencies and Integration Points
It depends on DVB frontend tuner ops, Linux I2C, optional demod `i2c_gate_ctrl`, and `tda826x.h`. It is used by DVB-S demod bridge drivers that need a legacy attach API.

## Risks and Edge Cases
The attach detection uses a zero-length write message, which not all I2C adapters support. Return values from gate control are ignored. Bandwidth math assumes rolloff 0.35 and adds margin; unusual symbol rates can over/under-filter. The sleep command changes loop-through power, so incorrect `has_loopthrough` board data affects RF pass-through.

## Test Signals
Tests should cover attach detection success/failure, I2C adapters that reject zero-length writes, loop-through and no-loop-through sleep bytes, frequency rounding, low/high symbol-rate bandwidth clamps, gate open/close sequencing, write errors, and release cleanup.

# sources/distributed-fs/ceph-client/drivers/comedi/drivers/c6xdigio.c

## Purpose
This legacy Comedi driver supports the Mechatronic Systems C6x_DIGIO DSP daughter card attached at a manually configured base address, typically on a parallel-port-like interface. It exposes two PWM output channels and two 24-bit encoder/counter input channels. The code includes optional PnP registration for standard and ECP printer ports, but actual Comedi attachment still uses the user-supplied I/O base.

## Important APIs, Types, and Functions
The hardware interface has data, status, and control offsets. `c6xdigio_chk_status()` polls bit 7 of the status register until it toggles away from the expected context or times out. `c6xdigio_write_data()` emits command/data bytes and waits for the handshake. `c6xdigio_pwm_write()` serializes a clamped PWM value in 2-bit chunks. `c6xdigio_encoder_read()` reads eight 3-bit chunks to assemble a 24-bit encoder value. Instruction handlers are `c6xdigio_pwm_insn_write()`, `c6xdigio_pwm_insn_read()`, and `c6xdigio_encoder_insn_read()`. `c6xdigio_init()` initializes PWM and resets encoders.

## Control Flow
Module init registers the Comedi driver and, when PnP is enabled, registers a minimal PnP driver for printer-port IDs while ignoring PnP registration failure. Attach requests a 3-byte I/O region at `it->options[0]`, allocates two subdevices, initializes the PWM subdevice as writable and the encoder subdevice as readable `SDF_LSAMPL`, and calls `c6xdigio_init()`. PWM writes clamp values to 2..498, send five two-bit payloads with alternating handshake status expectations, then send an idle command. PWM readback uses packed values in `s->state` rather than private storage. Encoder reads issue an encoder command, read 3 status bits per handshake phase, assemble a 24-bit value, and convert two's-complement hardware format to Comedi offset-binary via `comedi_offset_munge()`.

## State and Persistence Behavior
The driver has no private struct. PWM readback for two channels is packed into the PWM subdevice's `s->state` as two 16-bit fields. Encoder values are read directly from hardware and not cached. Hardware PWM and encoder state persists on the attached daughter card until reset or overwritten. The module-level `c6xdigio_pnp_registered` flag records whether PnP unregister is needed.

## Dependencies and Integration Points
It depends on legacy Comedi attach/detach, `comedi_check_request_region()`, low-level port I/O, optional Linux PnP APIs, and Comedi counter/PWM subdevice conventions. It does not use interrupts despite including interrupt headers.

## Risks
The busy-wait timeout is only 20 polling iterations and has no delay, so slow hardware can fail with `-EBUSY`. Several helper return values are ignored in PWM/encoder paths, so handshake errors may not propagate to users. `c6xdigio_pwm_insn_write()` appears to clear state with `s->state &= (0xffff << (16 * chan))`, which preserves the selected channel bits instead of preserving the other channel; that can corrupt packed readback. Attach calls init even if the daughter card is absent, as noted by the source comment.

## Test Signals
Test manual attach with valid and invalid I/O bases, handshake timeout behavior, PWM clamping and readback on both channels, packed readback preservation when channels are written alternately, encoder reads for positive and negative two's-complement values, init/reset command sequences, PnP registration failure tolerance, and module exit unregister ordering.

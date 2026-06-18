# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sunplus.c

## Purpose

`pwm-sunplus.c` drives the Sunplus SP7021 four-channel PWM block. It supports normal polarity only, outputs low when disabled, and applies new FREQ/DUTY settings immediately.

## APIs, control flow, and state

`struct sunplus_pwm` stores MMIO and clock. Apply rejects polarity changes, clears output/counter bits for disable, computes `dd_freq`, writes FREQ, computes 8-bit duty plus channel select, handles full duty via bypass/high output, and writes DUTY/MODE registers. `get_state()` reads mode/frequency/duty and reconstructs enabled period/duty.

There is no software state; the clock is enabled for device lifetime.

## Dependencies and integration points

It binds `sunplus,sp7021-pwm`, uses MMIO, an unnamed clock, managed clock cleanup, and the PWM core.

## Risks and test signals

FREQ then DUTY writes create a short mixed-setting window. Disable is immediate. Long periods saturate frequency. Polarity validation compares to current state. Test full-duty bypass, disable-low, readback, saturation, polarity rejection, and live-change glitches.

# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100_proc.h

## Purpose
`stb6100_proc.h` provides alternate static STB6100 wrapper helpers that open and close the demodulator I2C gate around tuner frequency/bandwidth operations.

## Important APIs, Types, and Functions
- `stb6100_get_freq()` and `stb6100_get_bandw()` wrap tuner getter calls with optional `frontend_ops->i2c_gate_ctrl(fe, 1)` before and `i2c_gate_ctrl(fe, 0)` after.
- `stb6100_set_freq()` and `stb6100_set_bandw()` use the same temporary `dtv_property_cache` mutation pattern as `stb6100_cfg.h`, but also gate the bus for `.set_params`.

## Control Flow
Each function checks whether the relevant tuner callback exists. If so, it enables the I2C gate when the demodulator provides `i2c_gate_ctrl`, performs the tuner operation, then disables the gate on success.

## State and Persistence Behavior
Setters temporarily clear the other tuning property (`bandwidth_hz` or `frequency`) so `.set_params` touches only the requested dimension. Hardware state is changed by the underlying tuner op. The demodulator I2C repeater/gate is a transient hardware side effect.

## Dependencies and Integration Points
This include-style helper depends on `struct dvb_frontend_ops`, `struct dvb_tuner_ops`, and the optional demodulator `.i2c_gate_ctrl` callback. It is intended for demodulator/board combinations where the tuner sits behind a gated I2C repeater.

## Risks and Edge Cases
On error paths, the functions return before closing the I2C gate, leaving the repeater enabled. `stb6100_set_freq()` also restores `bandwidth_hz` before checking the error, but does not close the gate if `.set_params` fails; similarly for bandwidth. Missing callbacks are treated as success.

## Test Signals
Fake frontend tests should assert gate open/close ordering for success and should expose the current leak on tuner callback failure. Hardware tests should validate that repeated get/set operations do not leave the bus in an unexpected state after I2C faults.

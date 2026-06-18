# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dib3000mb_priv.h

## Purpose
Provides the private register map, helper macros, default tables, and private state definition used by `dib3000mb.c`. It is the hardware-description companion for the DiB3000M-B demodulator implementation.

## Important APIs, Types, And Data
The header defines I2C helper macros `rd`, `wr`, `wr_foreach`, `set_or`, and `set_and`, debug macro `dprintk`, DVB-T numeric constants, tuner-write enable/disable encodings, vendor/device IDs, and `struct dib3000_state`. The state contains the I2C adapter, copied `dib3000_config`, `dvb_frontend`, timing-offset fields, and last tuned bandwidth/frequency.

Most of the file is register and table data: restart/control registers, FFT/guard/QAM/FEC/hierarchy fields, DDS/timing registers, bandwidth tables for 6/7/8 MHz, impulse-noise values, AGC gains/bandwidths, phase-noise values, lock masks, mobile/diversity/output/FIFO/PID parser registers, filter coefficients, power/clock/electrical-output registers, tuner pass-through register, and monitoring/TPS/BER/PER/lock/IRQ registers.

## Control Flow
The macros are expanded throughout `dib3000mb.c`. `wr()` returns `-EREMOTEIO` from the caller on failed writes, which shapes error handling in initialization and tuning. `wr_foreach()` writes register/value arrays in order and logs if array sizes differ.

## State And Persistence
The header's state struct is embedded in the implementation's heap allocation. Static tables live for module lifetime and are read-only in normal operation, although they are not declared `const`. Hardware persistence is represented by the register constants and values programmed by the C file.

## Dependencies And Integration Points
It depends on `dib3000.h` definitions, `struct i2c_adapter`, `struct dvb_frontend`, and the implementation-provided `debug`, `dib3000_read_reg()`, and `dib3000_write_reg()` symbols/macros. It is private to the MB implementation and should not be included by other drivers.

## Risks
Because this header defines non-const static arrays, including it in more than one C file would create duplicate mutable table copies. The `wr` macro contains control flow that returns from the containing function, so it is easy to misuse in contexts that need cleanup. Register names with `UNK` values document uncertainty; changing them without hardware validation is risky. `wr_foreach()` only logs size mismatch and then iterates over the register array length, so mismatched tables can still perform out-of-bounds reads of the value array.

## Test Signals
Compilation of `dib3000mb.c` is the main static test. Runtime signals are successful default initialization table writes, correct bandwidth table selection, valid monitoring register reads, and no `wr()` error returns during tune/init paths.

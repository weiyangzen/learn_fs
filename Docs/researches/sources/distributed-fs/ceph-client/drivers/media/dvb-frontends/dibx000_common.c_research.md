# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dibx000_common.c

## Purpose
`dibx000_common.c` implements shared I2C-master support for the DiBcom demodulator family. It turns demodulator-hosted GPIO/tuner I2C interfaces into Linux `i2c_adapter` instances and provides common speed, reset, init, and cleanup helpers for DiB3000/7000/8000/9000-family drivers.

## Important APIs, Types, and Functions
Exported functions are `dibx000_i2c_set_speed()`, `dibx000_get_i2c_adapter()`, `dibx000_reset_i2c_master()`, `dibx000_init_i2c_master()`, and `dibx000_exit_i2c_master()`. Internal helpers include `dibx000_write_word()`, `dibx000_read_word()`, `dibx000_is_i2c_done()`, `dibx000_master_i2c_write()`, `dibx000_master_i2c_read()`, `dibx000_i2c_select_interface()`, direct GPIO12/GPIO34 transfer functions, gated tuner/GPIO67 transfer functions, `dibx000_i2c_gate_ctrl()`, and `i2c_adapter_init()`.

## Control Flow
Initialization sets the demod revision, parent adapter, shifted I2C address, base register (`1024` for DiB7000P/DiB8000, otherwise `768`), registers four child adapters, closes the gate, and selects the tuner interface. Direct master transfers select GPIO12 or GPIO34 and then chunk reads or writes through demod FIFO/control registers in up to eight-byte pieces. Gated transfers select the target interface, build a combined parent I2C transaction that opens the gate, forwards the caller messages, then closes the gate.

## State and Persistence
Runtime state lives in `struct dibx000_i2c_master`: selected interface, registered child adapters, parent adapter/address, base register, transfer buffers, message array, and `i2c_buffer_lock`. There is no persistent storage; hardware gate/interface registers and speed divisors are volatile.

## Dependencies and Integration Points
The file depends on Linux I2C, mutexes, modules, and `dibx000_common.h`. It is integrated by demod drivers that embed `struct dibx000_i2c_master` and expose child I2C buses to tuner drivers. The exported speed function expects `i2c_get_adapdata()` to return the master object.

## Risks and Edge Cases
The transfer code returns `0` rather than a negative error from some child adapter paths when a chunk read/write fails, which I2C callers may interpret as no messages transferred. Gated paths reject more than 32 messages because the master has 34 `i2c_msg` slots. Speed calculation divides `60000 / speed`; invalid zero speed would fault. `dibx000_init_i2c_master()` logs adapter-registration failures but still continues and returns only the final gate-close transfer result, so partially registered adapter sets are possible. Lock interruption maps to `-EINVAL` in some helpers.

## Test Signals
Test child adapter registration/removal, direct GPIO12/GPIO34 reads and writes over multiple eight-byte chunks, gated tuner and GPIO67 transactions with open/close gate sequencing, interface switching, speed programming with old and new device revisions, reset closing the gate, error handling for NACK/timeouts, and cleanup after partial initialization.

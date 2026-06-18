# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-owl.c

## Purpose
Implements the Actions Semiconductor Owl SoC I2C controller driver for S500/S700/S900. It supports normal interrupt transfers and atomic polling transfers, repeated-start write-read operations, FIFO management, basic bus-busy checks, and clock-divider programming.

## Important APIs, Types, And Functions
`struct owl_i2c_dev` stores adapter, active message, completion, clock, spinlock, MMIO base, bus frequency, buffer index, and error. `owl_i2c_xfer_common()` implements the shared transfer path. `owl_i2c_xfer_data()` handles FIFO byte movement and error detection. `owl_i2c_interrupt()` completes interrupt-driven transactions. Probe maps resources, validates clock frequency, enables clock, requests IRQ, and registers the adapter.

## Control Flow
Each transfer resets the controller, sets frequency, resets FIFO, checks bus busy, clears arbitration-lost state, programs command flags, optionally writes internal address bytes for repeated-start transactions, preloads write data, configures NACK ignore, starts the command, and waits either for completion or by polling FIFO status. Errors send STOP/release bus and disable the controller at exit.

## State And Persistence
Transfer state is transient in `msg`, `msg_ptr`, and `err`. Hardware state is reset at each transfer and disabled afterward. The driver persists only adapter registration, clock rate, and selected bus frequency.

## Dependencies And Integration Points
Depends on platform/OF matching, clocks, IRQs, completions, spinlocks, I2C adapter quirks, and `readl_poll_timeout_atomic()` for atomic transfers. Adapter quirks allow combined write-first messages with first leg up to six bytes and message lengths up to 240 bytes.

## Risks
The FIFO read loop tests `RFE` as written by the hardware definition, so read semantics must match the controller documentation. Reset and bus-busy checks sleep, requiring lock release/reacquire boundaries. Atomic mode bypasses IRQ completion and depends on polling `CECB`/NACK bits. Only 100 kHz and 400 kHz are accepted.

## Test Signals
Exercise 100 kHz and 400 kHz transfers, single read/write, combined write-read with up to six address bytes, atomic transfers from contexts that require polling, NACK and bus-error handling, arbitration-lost return `-EAGAIN`, FIFO reset timeout, bus busy timeout, and probe validation for invalid clock-frequency.

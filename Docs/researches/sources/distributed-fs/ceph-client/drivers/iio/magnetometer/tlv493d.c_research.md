# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/tlv493d.c

## Purpose
I2C IIO driver for the Infineon TLV493D-A1B6 low-power 3D magnetic sensor. It supports direct raw reads and triggered buffers for X/Y/Z magnetic axes plus temperature.

## Important APIs, Types, And Functions
`struct tlv493d_data` stores the I2C client, access mutex, operating mode, and the write-register shadow required by the device's byte-stream protocol. `tlv493d_init()` reads reserved fields and seeds `wr_regs`. `tlv493d_set_operating_mode()` edits shadow mode bits and writes the entire write register stream. `tlv493d_get_measurements()` resumes the device, polls until the temperature channel validity bits indicate fresh data, decodes 12-bit signed fields, and autosuspends. `tlv493d_trigger_handler()` pushes buffered scans.

## Control Flow
Probe allocates IIO state, enables `vdd`, chooses master-controlled mode, initializes the register shadow, registers channels and a triggered buffer, enables runtime PM, and registers the IIO device. Direct reads and trigger reads both call the same measurement routine.

## State And Persistence
The driver keeps a shadow of all writable bytes because writes must start at address zero and omit register addresses. Runtime PM switches between powerdown and the configured mode. No nonvolatile state is written.

## Dependencies And Integration Points
Uses raw I2C byte streams, regulator APIs, runtime PM, IIO triggered buffers, and `read_poll_timeout()`. Matches `"infineon,tlv493d-a1b6"`.

## Risks And Test Signals
The unusual bus protocol makes register-shadow correctness critical. Poll timing depends on the selected operating mode. Test initialization reserved-bit preservation, PM suspend/resume, direct and triggered reads, scan mask layout, scale/offset reporting, and I2C short/error paths.

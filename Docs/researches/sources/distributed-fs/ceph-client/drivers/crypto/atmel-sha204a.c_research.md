# sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha204a.c

## Purpose

`atmel-sha204a.c` is the I2C driver for Microchip/Atmel ATSHA204/ATSHA204A devices. It exposes the device random command through the Linux hwrng framework and exports the OTP zone through a read-only sysfs attribute. It uses the shared `atmel-i2c` transport for wake, command, read, status handling, and queued asynchronous random reads.

## Important APIs, Types, And Functions

`atmel_sha204a_rng_read()` implements blocking and nonblocking hwrng reads. `atmel_sha204a_rng_read_nonblocking()` keeps at most one queued random command by using `tfm_count` and `rng->priv` to hold completed work data. `atmel_sha204a_rng_done()` stores completed async work for the next read and decrements the in-flight count. `atmel_sha204a_otp_read()` reads one OTP word, and `otp_show()` concatenates the 64-byte OTP zone as hex. Probe registers hwrng and sysfs group after `atmel_i2c_probe()`.

## Control Flow

Probe validates the secure element through the shared I2C probe, initializes the embedded hwrng with quality 1, registers it with devm hwrng, and creates `/sys/.../atsha204a/otp`. Blocking hwrng reads synchronously issue a random command and copy response data. Nonblocking reads either return data from the previous completed work item and queue the next request, or allocate/queue the first work item and return zero bytes. Removal unregisters hwrng, flushes the shared I2C queue, removes sysfs, and frees any cached work.

## State And Persistence Behavior

Per-client state is inherited from `struct atmel_i2c_client_priv`, including the hwrng object and `tfm_count` reused as a one-operation in-flight guard. `rng->priv` temporarily owns an allocated `atmel_i2c_work_data` containing the last random response. OTP content is persistent device state and is read on demand. The hwrng quality is deliberately set to 1 because the hardware RNG is considered low entropy.

## Dependencies And Integration Points

The driver depends on the I2C core, hwrng framework, sysfs attributes, shared Atmel I2C command helpers, workqueues, and OF/I2C IDs for `atmel,atsha204` and `atmel,atsha204a`.

## Risks And Test Signals

Risks include low entropy despite hwrng exposure, stale `rng->priv` work data after errors, concurrent remove/read interactions, OTP sysfs reads blocking for many I2C transactions, and response copying including count/status bytes rather than only random payload. Test hwrng blocking/nonblocking reads, sysfs OTP output length/content, queue flushing on remove, I2C random/read failures, and behavior under repeated short hwrng reads.

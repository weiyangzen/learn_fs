# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_gnss.c

## Purpose
Provides Linux GNSS subsystem support for the internal u-blox GNSS receiver found on supported E810T hardware. It exposes a `gnss_device`, polls the receiver through AdminQ I2C transactions, and forwards raw UBX data between userspace and hardware.

## Important APIs, types, and functions
- `ice_gnss_init()` allocates `struct gnss_serial`, starts a kthread worker, registers the GNSS device, and sets `ICE_FLAG_GNSS`.
- `ice_gnss_exit()` deregisters the GNSS device, clears the flag, cancels delayed work, destroys the worker, and frees state.
- `ice_gnss_is_module_present()` checks ownership of the source timer, netlist GPS support, and a PCA9575 presence bit.
- `ice_gnss_read()` is delayed work that reads the u-blox available-data length register, reads raw bytes in AdminQ I2C chunks, inserts them through `gnss_insert_raw()`, and requeues itself.
- `ice_gnss_write()` validates userspace writes and calls `ice_gnss_do_write()`.
- `ice_gnss_do_write()` chunks UBX writes around the hardware constraint that one-byte writes are not possible.
- `ice_gnss_open()` and `ice_gnss_close()` start and stop polling for a consumer.

## Control flow
Initialization creates per-PF GNSS state and registers GNSS operations. On open, polling begins immediately. Each read work item verifies the PF and feature flag, reads two big-endian length bytes from the u-blox register, skips empty reads, allocates a page buffer, reads up to a page of data using `ICE_MAX_I2C_DATA_SIZE` chunks, sends the data to the GNSS core, then requeues at either the fast poll interval or the normal message interval. Close and exit synchronously cancel the delayed work.

## State and persistence behavior
State lives in `pf->gnss_serial`, `pf->gnss_dev`, and `ICE_FLAG_GNSS`. The worker repeatedly requeues while enabled. No persistent host storage is used; hardware presence and data availability are polled from the adapter and receiver.

## Dependencies and integration points
Depends on the Linux GNSS subsystem, kthread delayed work, AdminQ I2C helpers (`ice_aq_read_i2c`, `ice_aq_write_i2c`), link topology addressing, PCA9575 GPIO access, timer ownership capability, and netlist GPS detection. It is invoked during probe/rebuild paths when `ice_gnss_is_module_present()` allows GNSS support.

## Risks
Polling and teardown races are mitigated by flag checks and synchronous cancellation, but any future caller must preserve that lifecycle. I2C write chunking is hardware-specific and easy to break; one-byte writes are explicitly invalid. The read path caps data to one page, so unexpectedly large receiver buffers are drained over multiple polls. Memory allocation failure causes a retry, not permanent disable.

## Test signals
Test with `CONFIG_GNSS` enabled and disabled, hardware-present and absent detection, userspace open/close loops, invalid write sizes (`0`, `1`, and above `ICE_GNSS_TTY_WRITE_BUF`), forced I2C errors, and raw UBX data flow through `/dev/gnss*`.

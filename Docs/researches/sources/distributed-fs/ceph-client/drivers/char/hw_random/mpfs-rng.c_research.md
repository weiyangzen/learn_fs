# sources/distributed-fs/ceph-client/drivers/char/hw_random/mpfs-rng.c

## Purpose
This driver exposes the Microchip PolarFire SoC system-controller RNG service through hwrng. It sends mailbox transactions to the MSS system controller and copies 32-byte responses into the hwrng buffer.

## Important APIs, Types, and Functions
- `struct mpfs_rng` stores the system-controller handle and hwrng.
- `mpfs_rng_read()` builds `mpfs_mss_msg`/`mpfs_mss_response`, calls `mpfs_blocking_transaction()`, and copies response bytes.
- `mpfs_rng_probe()` obtains the system controller and registers hwrng.

## Control Flow
Probe allocates state, gets the MPFS system-controller handle, sets read/name callbacks, and registers. Reads repeatedly issue command opcode `0x21` until `max` bytes are filled, unless `wait` is false, in which case a single response is copied.

## State and Persistence Behavior
The driver has no local hardware state; the system controller owns RNG state. Stack response buffers are copied to callers and discarded. The system-controller pointer persists for device lifetime.

## Dependencies and Integration Points
It depends on `POLARFIRE_SOC_SYS_CTRL`, `soc/microchip/mpfs.h`, platform device registration, and hwrng core.

## Risks
All entropy and blocking behavior depend on system-controller firmware. `buf + count` uses void-pointer arithmetic, accepted by GNU C but nonstandard. Transaction errors abort reads even after prior successful chunks in the same call.

## Test Signals
Test missing controller, transaction failure, blocking multi-response reads, nonblocking single-response reads, partial final copy sizes, and module unload through devm.

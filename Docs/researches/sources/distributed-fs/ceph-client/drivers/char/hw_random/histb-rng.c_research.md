# sources/distributed-fs/ceph-client/drivers/char/hw_random/histb-rng.c

## Purpose
This driver supports HiSilicon STB RNG hardware. It configures source, post-processing, drop mode, and post-processing depth, exposes the depth as a sysfs attribute, and reads available RNG words.

## Important APIs, Types, and Functions
- `struct histb_rng_priv` stores hwrng and MMIO base.
- `histb_rng_init()` programs source and post-processing depth.
- `histb_rng_wait()` polls `RNG_STAT.DATA_COUNT`.
- `histb_rng_read()` reads `RNG_NUMBER` for each requested word.
- `depth_show()`/`depth_store()` expose and reprogram depth.

## Control Flow
Probe maps MMIO, initializes depth to 144, waits for the first value, registers hwrng, and installs device groups. Reads check data count for each word, optionally wait up to 30 ms, and return partial bytes or timeout. Sysfs writes parse a depth and reinitialize the control register.

## State and Persistence Behavior
The programmed depth persists in the control register and can be changed at runtime. No software buffer exists. Driver data is stored on both platform and device.

## Dependencies and Integration Points
It depends on OF compatible `hisilicon,histb-rng`, hwrng core, platform MMIO, sysfs attribute groups, and relaxed polling helpers.

## Risks
`histb_rng_read()` increments by four bytes but tests `i < max`, so unaligned `max` values can write a full `u32` past the intended size; the core normally asks aligned buffer sizes but the provider is not defensive. Depth writes are not synchronized with concurrent reads.

## Test Signals
Test initial bring-up timeout, sysfs depth show/store, blocking and nonblocking reads, unaligned max handling in provider-level tests, and repeated depth changes while reading.

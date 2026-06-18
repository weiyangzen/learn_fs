
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda665x.c

## Purpose
`tda665x.c` implements a simple TDA665x terrestrial/cable tuner ops provider. It attaches to an existing frontend, programs PLL divider and band/current-selection bytes over I2C, reports cached frequency and PLL lock status, and exposes tuner metadata from board config.

## Important APIs, Types, and Functions
The exported API is `tda665x_attach()`. `struct tda665x_state` stores the parent frontend, I2C adapter, config, cached frequency, and bandwidth. Helpers include `tda665x_read()`, `tda665x_write()`, `tda665x_get_frequency()`, `tda665x_get_status()`, `tda665x_set_frequency()`, `tda665x_set_params()`, and `tda665x_release()`.

## Control Flow
Attach allocates state, stores config/I2C/frontend pointers, installs `tda665x_ops`, and copies tuner info from config. `set_params()` calls `tda665x_set_frequency()` with the frontend cached frequency. Frequency programming validates range, converts RF frequency through board offset/reference divider/multiplier, writes PLL bytes, selects low/mid/high band and charge-pump current based on frequency, waits 20 ms, checks PLL lock, and caches frequency on lock.

## State and Persistence Behavior
The driver keeps only volatile cached frequency and board config pointer. No standby callback is provided. PLL lock status is read from the tuner status byte, and cached frequency is updated only when lock is observed.

## Dependencies and Integration Points
It depends on DVB frontend tuner ops, Linux I2C, and `tda665x.h`. Board config supplies tuner name, I2C address, frequency limits, offset, and reference parameters.

## Risks and Edge Cases
The frequency range check appears inverted: it rejects when `new_frequency < frequency_max` or `new_frequency > frequency_min`, which would reject most normal values if min/max are conventional. `tda665x_set_frequency()` declares a 4-byte buffer but calls `tda665x_write()` with length 5, which is an out-of-bounds read risk. Several frequency thresholds use values like `1040000000` and `1250000000` in a path labeled VHF-L, likely typo-scale errors. The driver returns success even if lock is not achieved.

## Test Signals
Tests should explicitly cover frequency-range validation, buffer length under sanitizers, PLL programming bytes for VHF-L/VHF-H/UHF, lock and no-lock behavior, I2C read/write errors, tuner info propagation from config, and detach release.

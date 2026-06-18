# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-dvfs.c

## Purpose
`exynos-acpm-dvfs.c` builds ACPM DVFS commands for setting and querying firmware-managed clock rates.

## Important APIs And Functions
- `acpm_dvfs_set_xfer()` fills `struct acpm_xfer` with command buffers, channel ID, and optional response.
- `acpm_dvfs_init_set_rate_cmd()` encodes clock ID, rate in kHz, request type, and timestamp.
- `acpm_dvfs_set_rate()` sends a no-response frequency request.
- `acpm_dvfs_init_get_rate_cmd()` encodes a frequency-get request.
- `acpm_dvfs_get_rate()` sends the request and returns response rate converted from kHz to Hz.

## Control Flow
Clients call the ops installed by `exynos-acpm.c`. The helper fills a four-word command, assigns the ACPM channel, and calls `acpm_do_xfer()`. Set-rate ignores firmware response content, while get-rate expects the same command buffer to be updated and returns `xfer.rxd[1] * HZ_PER_KHZ`, or zero on transfer failure.

## State And Persistence
This file stores no persistent state. It asks ACPM firmware to change or report clock state; set-rate changes persist in firmware/hardware until later policy updates.

## Dependencies And Integration Points
It depends on the core ACPM transfer API, bitfield helpers, firmware protocol public header, and timekeeping for timestamps. It is installed into `acpm_handle.ops.dvfs_ops`.

## Risks
Rate conversion truncates to kHz for firmware and returns zero on transfer failure, which can also be a valid-looking rate sentinel to callers. Command format depends on firmware bitfield layout. The command buffer is stack-local and must remain valid only for the synchronous `acpm_do_xfer()` duration.

## Test Signals
Clock clients should be able to set rates and read back expected values through ACPM. Transfer errors from `acpm_do_xfer()` or zero get-rate responses indicate mailbox/firmware problems.

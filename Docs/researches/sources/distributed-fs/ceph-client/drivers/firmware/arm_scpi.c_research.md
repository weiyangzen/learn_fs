# sources/distributed-fs/ceph-client/drivers/firmware/arm_scpi.c

## Purpose
This file implements the ARM System Control and Power Interface mailbox protocol driver. It exposes a global `struct scpi_ops` through `get_scpi_ops()` so clock, DVFS, sensor, OPP, and device power-state consumers can call SCP firmware without knowing the mailbox/shared-memory framing. It supports both standard `arm,scpi` and legacy `arm,scpi-pre-1.0` firmware command layouts.

## Important APIs, Types, And Functions
Key state lives in `struct scpi_drvinfo`, which records protocol/firmware versions, command table, priority bitmap, channels, cached DVFS data, and exported ops. `struct scpi_chan` owns one mailbox channel, split TX/RX shared-memory windows, pending RX list, reusable transfer pool, token counter, and locks. `struct scpi_xfer` is the per-command transaction object.

The central path is `scpi_send_message()`: it selects a channel, allocates an xfer, packs command metadata, sends through `mbox_send_message()`, waits up to `MAX_RX_TIMEOUT`, maps SCPI status values to Linux errno, and returns the xfer to the pool. Firmware-facing callbacks are `scpi_tx_prepare()` and `scpi_handle_remote_msg()`, with `scpi_process_cmd()` matching replies by token/command for standard mode or FIFO head for legacy mode.

The exported operations include `scpi_clk_get_range()`, `scpi_clk_get_val()`, `scpi_clk_set_val()`, `scpi_dvfs_get_idx()`, `scpi_dvfs_set_idx()`, `scpi_dvfs_get_info()`, `scpi_dvfs_add_opps_to_device()`, sensor queries, and device power-state getters/setters. `scpi_probe()` wires device-tree mailboxes and `shmem` nodes, maps shared memory, initializes channels, selects legacy behavior, queries capabilities, and populates child devices.

## Control Flow, State, And Persistence
The driver is mostly stateless across boots, but it persists runtime state in the singleton `scpi_info`. DVFS information is lazily cached per domain in `scpi_info->dvfs[]` and freed on remove. Transfer objects are preallocated per channel and reused under `xfers_lock`; RX completions are coordinated with `rx_pending` under `rx_lock`. Standard mode round-robins channels with `atomic_t next_chan`; legacy mode uses a command-priority bitmap to choose channel 0 or 1.

## Dependencies And Integration Points
The file depends on mailbox, OF address parsing, platform bus, `dev_pm_opp`, spinlocks/mutexes/completions, and little-endian shared-memory structures. Integration points are device tree compatibles `arm,scpi`, `arm,scpi-pre-1.0`, SCP shared-memory compatibles, sysfs version attributes, and the `linux/scpi_protocol.h` consumer API.

## Risks And Test Signals
Primary risks are protocol mismatch, incorrect shared-memory sizing, reply timeout cleanup, and legacy command ordering. The driver mitigates malformed firmware responses with length clipping and zero-fill of short RX payloads, and maps unsupported legacy commands to `-EOPNOTSUPP`. Useful tests are DT probe with multiple channels, standard and legacy command framing, timeout removal from `rx_pending`, DVFS OPP sorting/removal on failure, and sensor 32-bit legacy value handling.

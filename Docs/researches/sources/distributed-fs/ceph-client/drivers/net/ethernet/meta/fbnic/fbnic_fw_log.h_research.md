# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw_log.h

## Purpose

`fbnic_fw_log.h` declares the firmware log cache layout and APIs. It defines the fixed log buffer size, debugfs print format, log entry structure, log container structure, readiness predicate, and init/free/enable/disable/write functions used by firmware parsing, debugfs, and devlink health paths.

## Important APIs, Types, And Functions

`FBNIC_FW_LOG_SIZE` is a 512 KiB buffer size. `FBNIC_FW_LOG_FMT` formats log index and Zephyr-like `DD:HH:MM:SS.MMM` firmware timestamp. `struct fbnic_fw_log_entry` stores list linkage, log index, timestamp, message length, and flexible message bytes. `struct fbnic_fw_log` stores buffer start/end pointers, size, list head, and spinlock. `fbnic_fw_log_ready(fbd)` checks whether `data_start` is non-NULL.

## Control Flow

The header has no runtime control flow beyond the readiness macro. It defines the contract implemented by `fbnic_fw_log.c` and consumed by callers before enabling, writing, or reading firmware logs.

## State And Persistence

The structures describe in-memory, per-device log state. Nothing is persisted to disk. The list entries live inside the vmalloc buffer owned by `struct fbnic_fw_log`.

## Dependencies And Integration Points

The header depends on Linux spinlock and integer types and forward-declares `struct fbnic_dev`. It is included by `fbnic.h`, `fbnic_fw_log.c`, `fbnic_fw.c`, `fbnic_debugfs.c`, and `fbnic_devlink.c`.

## Risks And Edge Cases

Changing `FBNIC_FW_LOG_FMT` can break debugfs consumers. Changing structure layout or buffer size affects circular allocation in `fbnic_fw_log_write()`. The flexible message array uses `__counted_by(len)`, so `len` must match allocated/stored bytes. Callers must check readiness before reading unless they intentionally want `-ENXIO`/error behavior.

## Test Signals

Useful validation includes build coverage with flexible array annotations, debugfs formatting, readiness before/after init/free, and wraparound behavior in the implementation. No executable tests were run for this research item.

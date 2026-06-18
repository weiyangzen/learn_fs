# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hldio.h

## Purpose
This header defines optional HLDIO state, declarations, debugfs hooks, and disabled-build stubs for HabanaLabs direct storage I/O.

## Important APIs, Types, And Functions
`struct hl_p2p_region` describes a PCI P2P aperture, allocated P2P memory, page array, device physical address, BAR offset, size, and BAR number. `struct hl_dio` stores P2P regions, per-CPU inflight counters, region count, and I/O enablement. `struct hl_dio_stats` describes intended statistics. The header declares `hl_dio_ssd2hl()`, P2P init/fini, DIO start/stop, HLDIO init/fini/ioctl, debugfs hooks, and `hl_device_supports_nvme()`.

## Control Flow
With `CONFIG_HL_HLDIO`, callers bind to real implementations. Without it, operations return `-EOPNOTSUPP` or `-ENOTTY`, while init/fini/debugfs stubs are no-ops. `hl_poll_timeout_condition()` provides a small sleep/poll loop with a timeout and memory barrier.

## State And Persistence
The header defines the shape of `hdev->hldio` state and P2P region lifetime. `io_enabled` is stored as `u8`, so synchronization is caller-defined.

## Dependencies And Integration Points
It uses Linux file, seq_file, ktime, delay, kernel, and errno headers, and forward-declared HabanaLabs device/context types. It integrates build-time Kconfig selection with call sites elsewhere in the driver.

## Risks
Enabled and disabled signatures must stay identical. The polling macro evaluates its condition multiple times, so side effects would be unsafe. `hl_dio_stats` exists but is not updated by the reviewed implementation.

## Test Signals
Build with and without `CONFIG_HL_HLDIO`, validate stub return codes, debugfs configurations, and polling timeout behavior.

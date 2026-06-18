# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_debugfs.c

## Purpose
`ixgbe_debugfs.c` provides debugfs controls for ixgbe adapters. It creates a driver-level debugfs directory and per-adapter files that allow privileged users to read/write raw device registers and trigger selected netdev operations such as TX timeout handling.

## Important APIs, Types, And Functions
- `ixgbe_dbg_init()` creates the top-level debugfs directory named after `ixgbe_driver_name`.
- `ixgbe_dbg_adapter_init()` creates a per-adapter directory using `pci_name(adapter->pdev)` and files `reg_ops` and `netdev_ops`.
- `ixgbe_dbg_adapter_exit()` and `ixgbe_dbg_exit()` remove per-adapter and driver-level debugfs trees.
- `ixgbe_dbg_common_ops_read()` formats the last command buffer with the adapter netdev name and returns it as a single non-partial read.
- `ixgbe_dbg_reg_ops_write()` parses `read <reg>` and `write <reg> <value>` commands, performs MMIO access through `IXGBE_READ_REG` and `IXGBE_WRITE_REG`, and logs results.
- `ixgbe_dbg_netdev_ops_write()` parses `tx_timeout` and invokes `ndo_tx_timeout()`.
- `ixgbe_dbg_reg_ops_fops` and `ixgbe_dbg_netdev_ops_fops` wire the debugfs files to simple open/read/write operations.

## Control Flow
Module initialization creates the root directory. Adapter probe/start creates per-device entries with `adapter` as private data. Reads are allowed only from offset zero and allocate a formatted string with `kasprintf`; too-small user buffers return `-ENOSPC`. Writes are also only accepted at offset zero, bounded to 255 bytes plus terminator, copied with `simple_write_to_buffer`, parsed with `strncmp` and `sscanf`, then executed or logged as unknown commands. Adapter or module teardown removes debugfs entries recursively.

## State And Persistence
The file stores `ixgbe_dbg_root` and two static command buffers, `ixgbe_dbg_reg_ops_buf` and `ixgbe_dbg_netdev_ops_buf`. These buffers are global across adapters, so the last command is shared rather than per-adapter. Debugfs entries are runtime kernel objects and do not persist across module unload or reboot. Register writes mutate live hardware state immediately.

## Dependencies And Integration Points
The file depends on Linux debugfs, module file operations, simple buffer helpers, PCI naming, ixgbe adapter structures, netdev operations, and ixgbe MMIO/logging macros. It integrates with driver module init/exit and adapter probe/remove flows.

## Risks
- `reg_ops` exposes raw MMIO reads/writes to privileged debugfs users; incorrect writes can hang or misconfigure hardware.
- Static command buffers are shared among adapters and lack explicit locking, so concurrent debugfs writes can race and produce misleading readback/log messages.
- `tx_timeout` directly invokes the netdev timeout handler and can interfere with normal service/reset paths.
- File permissions are `0600`, but risk remains if debugfs is mounted and accessible to privileged automation.
- Buffer parsing is simple and accepts hex offsets/values without register-range validation.

## Test Signals
Signals include debugfs root and per-adapter file creation/removal, successful non-partial reads, `-ENOSPC` for oversized reads/writes, raw register read returning expected values, controlled write/readback on harmless scratch or documented registers, `tx_timeout` triggering the expected recovery path, teardown with open debugfs files, and concurrency smoke tests across multiple adapters.

# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_smbus.c

## Purpose

`rmi_smbus.c` implements the SMBus transport adapter for RMI4 touchpads, especially devices sharing PS/2 and SMBus behavior. It maps RMI register addresses to SMBus command codes through the SMBus v2 mapping table and registers the resulting transport with the RMI core.

## Important APIs, Types, and Functions

`struct mapping_table_entry` is the on-device 4-byte address/readcount/write-enable mapping entry. `struct rmi_smb_xport` stores the transport, I2C client, mapping table state, table index, and mutexes. Key functions include `rmi_smb_get_version()`, `rmi_smb_get_command_code()`, `rmi_smb_write_block()`, `rmi_smb_read_block()`, `rmi_smb_clear_state()`, `rmi_smb_enable_smbus_mode()`, `rmi_smb_reset()`, probe/remove, and PM callbacks.

## Control Flow

Probe requires platform data, SMBus block-read and host-notify functionality, and a valid IRQ. It allocates state, initializes locks, copies platform data, enables SMBus mode by reading the protocol version, then registers the transport. Reads and writes lock `page_mutex`, split transfers into up to 32-byte chunks, acquire or install a command-code mapping under `mappingtable_mutex`, then issue SMBus block transfers. Reset clears the local mapping table and re-enables SMBus mode without issuing an RMI reset command. Resume resets SMBus mapping, calls `rmi_reset()`, then resumes the RMI driver.

## State and Persistence Behavior

The transport persists a local mirror of the eight-entry SMBus mapping table and a round-robin replacement index. On reset, the mapping table is discarded. Runtime hardware state includes the device's command mapping table and SMBus mode activation.

## Dependencies and Integration Points

The file depends on I2C/SMBus APIs, platform RMI data, PM helpers, RMI transport registration, and RMI reset/suspend/resume helpers. It integrates with systems where PS/2 reset sequencing owns the physical reset and SMBus must avoid racing it.

## Risks and Edge Cases

The write loop computes `block_len` from total `len` instead of remaining `cur_len`, so final partial writes can be oversized when `len > 32` and not a multiple of 32. Read return length from `i2c_smbus_read_block_data()` is not checked against the requested length. The mapping table is only eight entries, so churn can hurt performance or expose stale mapping behavior if device writes fail. Probe cannot use firmware/OF data alone because it requires platform data.

## Test Signals

Tests should cover SMBus protocol versions 2 and 3, invalid versions, reads/writes at different RMI addresses and lengths, multi-chunk and final-partial writes, mapping-table reuse and wraparound, reset/resume clearing mappings, missing IRQ/platform data failures, and host-notify interrupt-driven RMI operation.

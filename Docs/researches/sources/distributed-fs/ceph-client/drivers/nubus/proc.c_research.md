# sources/distributed-fs/ceph-client/drivers/nubus/proc.c

## Purpose
Implements procfs views for NuBus board and resource information. It provides `/proc/nubus`, `/proc/bus/nubus/devices`, and optional per-board resource trees that mirror NuBus ROM resource directories.

## Important APIs, Types, And Functions
- `nubus_devices_proc_show()` prints each functional resource's slot, category/type/software/hardware ids, and slot address.
- `nubus_proc_add_board()` creates a board slot directory if resource procfs population is enabled.
- `nubus_proc_add_rsrc_dir()` creates resource subdirectories and stores bytelane data as parent private data.
- `struct nubus_proc_pde_data` records resource pointer and size, or a small inline integer resource.
- `nubus_proc_rsrc_show()` emits resource memory through `nubus_seq_write_rsrc_mem()` or emits a 3-byte integer resource.
- `nubus_proc_add_rsrc_mem()` / `nubus_proc_add_rsrc()` create per-resource proc files.
- `nubus_proc_init()` creates the top-level proc entries.

## Control Flow
NuBus init calls `nubus_proc_init()`. During ROM parsing, `nubus.c` calls the add helpers as it discovers boards, directories, and resources. The helpers no-op unless `/proc/bus/nubus` exists and `nubus_populate_procfs` is enabled. Reads dispatch through `single_open()` and `seq_read()`.

## State And Persistence
Proc directory pointer `proc_bus_nubus_dir` persists after init. Per-resource proc entries store heap-allocated `nubus_proc_pde_data`, but this file does not define an explicit release callback for that private data. Resource data points into slot ROM addresses or stores small integer values in the pointer field.

## Dependencies And Integration Points
Depends on procfs, seq_file, NuBus resource traversal helpers from `nubus.c`, and `nubus_populate_procfs`. It also uses parent proc private data to recover bytelanes for resource memory reads.

## Risks And Edge Cases
- Per-resource `nubus_proc_pde_data` allocations may not be explicitly freed when proc entries are removed.
- `nubus_proc_rsrc_show()` returns `-EFBIG` if the resource size exceeds the current seq buffer, so large resources may not be readable.
- Integer resources are emitted as raw bytes, not formatted text.
- The proc resource tree is deprecated/disabled by default because some ROMs make it expensive.

## Test Signals
With procfs enabled, `/proc/nubus` and `/proc/bus/nubus/devices` should exist. With `nubus.populate_procfs=1`, per-slot resource directories and files should appear and resource reads should match ROM data.
